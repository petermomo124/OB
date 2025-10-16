document.addEventListener('DOMContentLoaded', function() {
    // Function to handle the AJAX request
    function updateLeaveStatus(leaveId, action) {
        const formData = new FormData();
        formData.append('action', action);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        fetch(`/admin/attendance/leaverequest/${leaveId}/change/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                const messageDiv = document.createElement('div');
                messageDiv.className = 'alert alert-success alert-dismissible fade show';
                messageDiv.role = 'alert';
                messageDiv.innerHTML = `
                    ${data.message}
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                `;
                
                const container = document.querySelector('#content').querySelector('.container-fluid:first-child');
                container.insertBefore(messageDiv, container.firstChild);
                
                // Reload the page after a short delay to show the updated status
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing your request.');
        });
    }

    // Add click handlers for approve buttons
    document.querySelectorAll('.approve-leave').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to approve this leave request?')) {
                const leaveId = this.getAttribute('data-id');
                updateLeaveStatus(leaveId, 'approve');
            }
        });
    });

    // Add click handlers for reject buttons
    document.querySelectorAll('.reject-leave').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const notes = prompt('Please enter the reason for rejection:');
            if (notes !== null) {
                const leaveId = this.getAttribute('data-id');
                const formData = new FormData();
                formData.append('action', 'reject');
                formData.append('response_notes', notes);
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                fetch(`/admin/attendance/leaverequest/${leaveId}/change/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Error: ' + (data.error || 'Unknown error occurred'));
                    }
                });
            }
        });
    });
});
