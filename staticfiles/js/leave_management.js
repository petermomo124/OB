// Function to get CSRF token
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to show toast message
function showToast(message, type = 'info') {
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>`;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Function to update leave status
async function updateLeaveStatus(leaveId, status, button, notes = '') {
    const originalHTML = button ? button.innerHTML : '';
    
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }

    try {
        const response = await fetch(`/attendance/leave-request/${leaveId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                status: status,
                notes: notes
            })
        });

        const data = await response.json();
        
        if (data.success) {
            showToast(`Leave request has been ${status} successfully`, 'success');
            // Reload the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error(data.message || 'Failed to update leave status');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message || 'An error occurred. Please try again.', 'danger');
        if (button) {
            button.disabled = false;
            button.innerHTML = originalHTML;
        }
    }
}

// Function to delete leave request
async function deleteLeaveRequest(leaveId, button) {
    const originalHTML = button ? button.innerHTML : '';
    
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }

    try {
        const response = await fetch(`/attendance/leave-request/${leaveId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            showToast('Leave request deleted successfully', 'success');
            // Remove the row from the table
            const row = button ? button.closest('tr') : null;
            if (row) {
                row.style.opacity = '0';
                setTimeout(() => {
                    row.remove();
                }, 300);
            } else {
                window.location.reload();
            }
        } else {
            throw new Error(data.message || 'Failed to delete leave request');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message || 'An error occurred. Please try again.', 'danger');
        if (button) {
            button.disabled = false;
            button.innerHTML = originalHTML;
        }
    }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Handle view button click
    document.addEventListener('click', function(e) {
        if (e.target.closest('.view-leave-request')) {
            e.preventDefault();
            const button = e.target.closest('.view-leave-request');
            const leaveId = button.dataset.leaveId;
            window.location.href = `/attendance/leave-request/${leaveId}/`;
        }
    });

    // Handle approve button click
    document.addEventListener('click', function(e) {
        if (e.target.closest('.approve-leave-request')) {
            e.preventDefault();
            const button = e.target.closest('.approve-leave-request');
            const leaveId = button.dataset.leaveId;
            
            if (confirm('Are you sure you want to approve this leave request?')) {
                updateLeaveStatus(leaveId, 'approved', button);
            }
        }
    });

    // Handle reject button click
    document.addEventListener('click', function(e) {
        if (e.target.closest('.reject-leave-request')) {
            e.preventDefault();
            const button = e.target.closest('.reject-leave-request');
            const leaveId = button.dataset.leaveId;
            const reason = prompt('Please enter the reason for rejection:');
            
            if (reason !== null) {
                updateLeaveStatus(leaveId, 'rejected', button, reason);
            }
        }
    });

    // Handle delete button click
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-leave-request')) {
            e.preventDefault();
            const button = e.target.closest('.delete-leave-request');
            const leaveId = button.dataset.leaveId;
            
            if (confirm('Are you sure you want to delete this leave request? This action cannot be undone.')) {
                deleteLeaveRequest(leaveId, button);
            }
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
