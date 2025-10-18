import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class IPAPIService:
    """
    Service for IPAPI.co location service
    Free: 1,000 requests per day
    """

    BASE_URL = "https://ipapi.co"

    @staticmethod
    def get_client_location(request=None, ip_address=None):
        """
        Get location using IPAPI.co
        Priority: 1. Specific IP 2. Client IP from request 3. Auto-detected IP

        Returns: dict with location data or None if failed
        """
        try:
            # Build URL based on available data
            if ip_address:
                url = f"{IPAPIService.BASE_URL}/{ip_address}/json/"
            elif request:
                # Get client IP from request
                client_ip = IPAPIService._get_client_ip(request)
                if client_ip:
                    url = f"{IPAPIService.BASE_URL}/{client_ip}/json/"
                else:
                    url = f"{IPAPIService.BASE_URL}/json/"
            else:
                url = f"{IPAPIService.BASE_URL}/json/"

            # Check cache first (cache for 1 hour to save API calls)
            cache_key = f"ipapi_location_{url}"
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Using cached IPAPI location data for {url}")
                return cached_data

            # Make API request
            headers = {
                'User-Agent': 'FieldWorkApp/1.0'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check for API errors
                if data.get('error'):
                    logger.warning(f"IPAPI error: {data.get('reason')}")
                    return None

                # Format the response for our app
                location_data = IPAPIService._format_location_data(data)

                # Cache successful response for 1 hour
                cache.set(cache_key, location_data, 3600)

                logger.info(f"IPAPI location success: {location_data.get('address', 'Unknown')}")
                return location_data

            elif response.status_code == 429:
                logger.warning("IPAPI quota exceeded - rate limited")
                return {'error': 'quota_exceeded'}
            else:
                logger.error(f"IPAPI HTTP error: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            logger.error("IPAPI request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"IPAPI request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in IPAPI service: {str(e)}")
            return None

    @staticmethod
    def _get_client_ip(request):
        """
        Extract client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def _format_location_data(ipapi_data):
        """
        Format IPAPI response to match our app's expected format
        """
        return {
            'source': 'ipapi',
            'lat': ipapi_data.get('latitude'),
            'lng': ipapi_data.get('longitude'),
            'address': IPAPIService._build_address_string(ipapi_data),
            'accuracy': 5000,  # IP-based location accuracy estimate (in meters)
            'ip': ipapi_data.get('ip'),
            'city': ipapi_data.get('city'),
            'region': ipapi_data.get('region'),
            'country': ipapi_data.get('country_name'),
            'postal_code': ipapi_data.get('postal'),
            'timezone': ipapi_data.get('timezone'),
            'raw_data': ipapi_data  # Keep original data for debugging
        }

    @staticmethod
    def _build_address_string(ipapi_data):
        """
        Build a readable address string from IPAPI data
        """
        address_parts = []

        if ipapi_data.get('city'):
            address_parts.append(ipapi_data['city'])
        if ipapi_data.get('region'):
            address_parts.append(ipapi_data['region'])
        if ipapi_data.get('country_name'):
            address_parts.append(ipapi_data['country_name'])
        if ipapi_data.get('postal'):
            address_parts.append(ipapi_data['postal'])

        if address_parts:
            return ', '.join(address_parts)
        else:
            return f"Location from IP {ipapi_data.get('ip', 'Unknown')}"

    @staticmethod
    def get_remaining_quota_estimate():
        """
        Estimate remaining daily quota (rough estimate)
        In production, you might want to track this more precisely
        """
        # Count cache keys to estimate usage
        # This is a simple estimation - you might want to implement proper tracking
        return 800  # Conservative estimate