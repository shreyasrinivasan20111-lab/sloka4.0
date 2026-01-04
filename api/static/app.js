$(document).ready(function() {
    // State management
    let currentUser = null;
    let userType = null;
    let token = localStorage.getItem('token');
    let currentTab = 'courses';
    
    // Initialize app
    init();
    
    function init() {
        checkAuthentication();
        bindEvents();
        loadPublicCourses();
    }
    
    function checkAuthentication() {
        if (token) {
            // Verify token is still valid by making a test request
            const payload = parseJWT(token);
            if (payload && payload.exp * 1000 > Date.now()) {
                currentUser = payload.sub;
                userType = payload.type;
                updateUIForLoggedInUser();
                if (userType === 'student') {
                    showStudentDashboard();
                } else if (userType === 'admin') {
                    showAdminDashboard();
                }
            } else {
                logout();
            }
        }
    }
    
    function parseJWT(token) {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
        }
    }
    
    function updateUIForLoggedInUser() {
        $('#auth-buttons').hide();
        $('#user-menu').show();
        $('#user-email').text(currentUser);
        $('#welcome-section').hide();
        
        // Show appropriate dashboard based on user type
        if (userType === 'admin') {
            showAdminDashboard();
        } else {
            showStudentDashboard();
        }
    }
    
    function updateUIForLoggedOutUser() {
        $('#auth-buttons').show();
        $('#user-menu').hide();
        $('#student-dashboard').hide();
        $('#admin-dashboard').hide();
        $('#welcome-section').show();
        $('#courses-section').show();
    }
    
    function bindEvents() {
        // Navigation events
        $('#login-btn').click(() => openModal('#login-modal'));
        $('#register-btn').click(() => openModal('#register-modal'));
        $('#logout-btn').click(logout);
        $('#explore-courses-btn').click(() => {
            $('html, body').animate({
                scrollTop: $('#courses-section').offset().top - 100
            }, 500);
        });
        
        // Modal events - use event delegation for dynamically created modals
        $(document).on('click', '.close', function() {
            closeModal($(this).closest('.modal'));
        });
        
        $(window).click(function(event) {
            if ($(event.target).hasClass('modal')) {
                closeModal($(event.target));
            }
        });
        
        // Form events
        $('#login-form').submit(handleLogin);
        $('#register-form').submit(handleRegister);
        $('#course-form').submit(handleCourseForm);
        
        // Admin events
        $('.tab-btn').click(function() {
            switchTab($(this).data('tab'));
        });
        
        $('#add-course-btn').click(openAddCourseModal);
        $('#enroll-student-btn').click(enrollStudent);
        $('#remove-enrollment-btn').click(removeEnrollment);
        
        // Enrollment dropdowns
        $('#enrollment-course').change(loadCourseStudents);
    }
    
    // Authentication functions
    function handleLogin(e) {
        e.preventDefault();
        
        const email = $('#login-email').val();
        const password = $('#login-password').val();
        const isAdmin = $('#login-admin').is(':checked');
        
        // Basic validation with visual feedback
        if (!email || !password) {
            showToast('Please fill in all fields', 'error');
            
            // Add visual feedback to empty fields
            if (!email) {
                $('#login-email').closest('.form-group').addClass('error');
                setTimeout(() => $('#login-email').closest('.form-group').removeClass('error'), 3000);
            }
            if (!password) {
                $('#login-password').closest('.form-group').addClass('error');
                setTimeout(() => $('#login-password').closest('.form-group').removeClass('error'), 3000);
            }
            return;
        }
        
        if (!isValidEmail(email)) {
            showToast('Please enter a valid email address', 'error');
            $('#login-email').closest('.form-group').addClass('error');
            setTimeout(() => $('#login-email').closest('.form-group').removeClass('error'), 3000);
            return;
        }
        
        const endpoint = isAdmin ? '/api/auth/admin/login' : '/api/auth/student/login';
        const data = { email, password };
        
        showLoading();
        
        $.ajax({
            url: endpoint,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                hideLoading();
                token = response.access_token;
                localStorage.setItem('token', token);
                
                const payload = parseJWT(token);
                currentUser = payload.sub;
                userType = payload.type;
                
                updateUIForLoggedInUser();
                closeModal('#login-modal');
                showToast('Welcome back!', 'success');
                
                if (userType === 'student') {
                    showStudentDashboard();
                } else {
                    showAdminDashboard();
                }
            },
            error: function(xhr) {
                hideLoading();
                let errorMessage = 'Login failed. Please try again.';
                
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    errorMessage = xhr.responseJSON.detail;
                } else if (xhr.status === 401) {
                    if (isAdmin) {
                        errorMessage = 'Invalid admin credentials. Please check your email and password.';
                    } else {
                        errorMessage = 'Invalid login credentials. Please check your email and password, or register if you don\'t have an account.';
                    }
                } else if (xhr.status === 500) {
                    errorMessage = 'Server error occurred. Please try again in a few moments.';
                } else if (xhr.status === 0) {
                    errorMessage = 'Unable to connect to server. Please check your internet connection.';
                }
                
                showToast(errorMessage, 'error', 6000); // Show for 6 seconds for longer messages
                
                // Add helpful suggestions for common issues
                if (errorMessage.includes('No account found')) {
                    setTimeout(() => {
                        showToast('💡 Tip: You can register for a new account using the Register tab', 'info', 4000);
                    }, 2000);
                } else if (errorMessage.includes('password')) {
                    setTimeout(() => {
                        showToast('💡 Tip: Password is case-sensitive. Check your Caps Lock', 'info', 4000);
                    }, 2000);
                }
            }
        });
    }
    
    function handleRegister(e) {
        e.preventDefault();
        
        const email = $('#register-email').val();
        const password = $('#register-password').val();
        
        // Basic validation
        if (!email || !password) {
            showToast('Please fill in all fields', 'error');
            return;
        }
        
        if (!isValidEmail(email)) {
            showToast('Please enter a valid email address', 'error');
            return;
        }
        
        if (password.length < 6) {
            showToast('Password must be at least 6 characters long', 'error');
            return;
        }
        
        showLoading();
        
        $.ajax({
            url: '/api/auth/student/register',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email, password }),
            success: function(response) {
                hideLoading();
                closeModal('#register-modal');
                showToast('Account created successfully! Please log in.', 'success');
                openModal('#login-modal');
            },
            error: function(xhr) {
                hideLoading();
                const error = xhr.responseJSON?.detail || 'Registration failed. Please try again.';
                showToast(error, 'error');
            }
        });
    }
    
    function logout() {
        token = null;
        currentUser = null;
        userType = null;
        localStorage.removeItem('token');
        updateUIForLoggedOutUser();
        showToast('Logged out successfully', 'success');
    }
    
    // Dashboard functions
    function showStudentDashboard() {
        $('#welcome-section').hide();
        $('#admin-dashboard').hide();
        $('#student-dashboard').show();
        $('#courses-section').hide();
        loadStudentCourses();
    }
    
    function showAdminDashboard() {
        $('#welcome-section').hide();
        $('#student-dashboard').hide();
        $('#admin-dashboard').show();
        $('#courses-section').hide();
        loadAdminData();
    }
    
    function switchTab(tabName) {
        currentTab = tabName;
        $('.tab-btn').removeClass('active');
        $(`.tab-btn[data-tab="${tabName}"]`).addClass('active');
        
        $('.tab-content').removeClass('active');
        $(`#admin-${tabName}-tab`).addClass('active');
        
        if (tabName === 'students') {
            loadStudents();
        } else if (tabName === 'enrollments') {
            loadEnrollmentData();
        } else if (tabName === 'courses') {
            loadAdminCourses();
        }
    }
    
    // Data loading functions
    function loadPublicCourses() {
        $.ajax({
            url: '/api/courses',
            method: 'GET',
            success: function(courses) {
                renderPublicCourses(courses);
            },
            error: function() {
                showToast('Failed to load courses', 'error');
            }
        });
    }
    
    function loadStudentCourses() {
        $.ajax({
            url: '/api/student/courses',
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function(courses) {
                renderStudentCourses(courses);
            },
            error: function() {
                showToast('Failed to load your courses', 'error');
            }
        });
    }
    
    function loadAdminData() {
        loadAdminCourses();
    }
    
    function loadAdminCourses() {
        $.ajax({
            url: '/api/admin/courses',
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function(courses) {
                renderAdminCourses(courses);
            },
            error: function() {
                showToast('Failed to load courses', 'error');
            }
        });
    }
    
    function loadStudents() {
        $.ajax({
            url: '/api/admin/students',
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function(students) {
                renderStudents(students);
            },
            error: function() {
                showToast('Failed to load students', 'error');
            }
        });
    }
    
    function loadEnrollmentData() {
        // Load students for dropdown
        $.ajax({
            url: '/api/admin/students',
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function(students) {
                populateStudentDropdown(students);
            }
        });
        
        // Load courses for dropdown
        $.ajax({
            url: '/api/admin/courses',
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function(courses) {
                populateCourseDropdown(courses);
            }
        });
    }
    
    function loadCourseStudents() {
        const courseId = $('#enrollment-course').val();
        if (!courseId) {
            $('#course-students').empty();
            return;
        }
        
        $.ajax({
            url: `/api/admin/courses/${courseId}/students`,
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function(students) {
                renderCourseStudents(students, courseId);
            },
            error: function() {
                showToast('Failed to load course students', 'error');
            }
        });
    }
    
    // Rendering functions
    function renderPublicCourses(courses) {
        const container = $('#public-courses');
        container.empty();
        
        if (courses.length === 0) {
            container.html('<p class="text-center">No courses available at the moment.</p>');
            return;
        }
        
        courses.forEach(course => {
            const courseCard = createCourseCard(course, false);
            container.append(courseCard);
        });
    }
    
    function renderStudentCourses(courses) {
        const container = $('#student-courses');
        container.empty();
        
        if (courses.length === 0) {
            container.html(`
                <div class="course-card">
                    <div class="course-title">Welcome to Your Spiritual Journey</div>
                    <div class="course-description">You haven't enrolled in any courses yet. Contact your administrator to get started on your path of learning and growth.</div>
                </div>
            `);
            return;
        }
        
        courses.forEach(course => {
            const courseCard = createCourseCard(course, true);
            container.append(courseCard);
        });
    }
    
    function renderAdminCourses(courses) {
        const container = $('#admin-courses');
        container.empty();
        
        console.log('Rendering admin courses:', courses);
        
        if (courses.length === 0) {
            container.html('<p class="text-center">No courses created yet.</p>');
            return;
        }
        
        courses.forEach(course => {
            console.log('Creating admin card for course:', course);
            const courseCard = createAdminCourseCard(course);
            container.append(courseCard);
        });
    }
    
    function renderStudents(students) {
        const container = $('#admin-students');
        container.empty();
        
        if (students.length === 0) {
            container.html('<p class="text-center">No students registered yet.</p>');
            return;
        }
        
        students.forEach(student => {
            const studentCard = createStudentCard(student);
            container.append(studentCard);
        });
    }
    
    function renderCourseStudents(students, courseId) {
        const container = $('#course-students');
        container.empty();
        
        if (students.length === 0) {
            container.html('<p class="text-center">No students enrolled in this course.</p>');
            return;
        }
        
        students.forEach(student => {
            const studentCard = createCourseStudentCard(student, courseId);
            container.append(studentCard);
        });
    }
    
    // Card creation functions
    function createCourseCard(course, isStudent = false) {
        const metaItems = [];
        if (course.instructor) metaItems.push(`<div class="course-meta-item">Instructor: ${course.instructor}</div>`);
        if (course.duration) metaItems.push(`<div class="course-meta-item">Duration: ${course.duration}</div>`);
        if (course.sections) metaItems.push(`<div class="course-meta-item">Sections: ${course.sections.length}</div>`);
        
        // Create sections display
        let sectionsHTML = '';
        if (course.sections && course.sections.length > 0) {
            sectionsHTML = '<div class="course-sections">';
            course.sections.forEach((section, index) => {
                sectionsHTML += `
                    <div class="course-section">
                        <div class="section-title">${section.title}</div>
                        ${section.description ? `<div class="section-description">${section.description}</div>` : ''}
                        ${section.documents && section.documents.length > 0 ? `
                            <div class="section-documents">
                                ${section.documents.map(doc => 
                                    `<a href="#" onclick="previewMedia('${encodeURIComponent(doc.file_url)}', '${encodeURIComponent(doc.title)}', '${doc.file_type}')" class="document-link ${doc.file_type === 'audio' ? 'audio' : 'document'}">
                                        ${doc.file_type === 'audio' ? '🎵' : '📄'} ${doc.title}
                                    </a>`
                                ).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            sectionsHTML += '</div>';
        }
        
        return $(`
            <div class="course-card">
                <div class="course-title">${course.title}</div>
                <div class="course-description">${course.description || 'A journey of spiritual growth and learning.'}</div>
                ${course.content ? `<div class="course-content">${course.content}</div>` : ''}
                <div class="course-meta">
                    ${metaItems.join('')}
                </div>
                ${sectionsHTML}
                ${isStudent ? '<div class="course-actions"><span class="btn btn-outline" style="cursor: default;">Enrolled ✓</span></div>' : ''}
            </div>
        `);
    }
    
    function createAdminCourseCard(course) {
        console.log('createAdminCourseCard called with:', course);
        
        const metaItems = [];
        if (course.instructor) metaItems.push(`<div class="course-meta-item">Instructor: ${course.instructor}</div>`);
        if (course.duration) metaItems.push(`<div class="course-meta-item">Duration: ${course.duration}</div>`);
        if (course.sections) metaItems.push(`<div class="course-meta-item">Sections: ${course.sections.length}</div>`);
        metaItems.push(`<div class="course-meta-item">Students: ${course.students?.length || 0}</div>`);
        
        // Create sections preview
        let sectionsPreview = '';
        if (course.sections && course.sections.length > 0) {
            const totalDocs = course.sections.reduce((sum, section) => sum + (section.documents?.length || 0), 0);
            sectionsPreview = `<div class="sections-preview">${totalDocs} documents across ${course.sections.length} sections</div>`;
        }
        
        const cardHtml = `
            <div class="course-card admin-card">
                <div class="course-title">${course.title}</div>
                <div class="course-description">${course.description || 'No description provided.'}</div>
                ${course.content ? `<div class="course-content" style="margin-top: 10px; font-style: italic;">${course.content}</div>` : ''}
                <div class="course-meta">
                    ${metaItems.join('')}
                </div>
                ${sectionsPreview}
                <div class="course-actions">
                    <button class="btn btn-outline btn-manage-sections" data-id="${course.id}">Manage Sections</button>
                    <button class="btn btn-outline btn-edit-course" data-id="${course.id}">Edit</button>
                    <button class="btn btn-danger btn-delete-course" data-id="${course.id}">Delete</button>
                </div>
            </div>
        `;
        
        console.log('Generated admin card HTML:', cardHtml);
        return $(cardHtml);
    }
    
    function createStudentCard(student) {
        return $(`
            <div class="student-card">
                <div class="card-title">${student.email}</div>
                <div class="card-subtitle">Enrolled Courses: ${student.courses?.length || 0}</div>
                <div class="card-subtitle">Member since: ${new Date(student.created_at).toLocaleDateString()}</div>
            </div>
        `);
    }
    
    function createCourseStudentCard(student, courseId) {
        return $(`
            <div class="student-card">
                <div class="card-title">${student.email}</div>
                <div class="card-subtitle">Member since: ${new Date(student.created_at).toLocaleDateString()}</div>
                <div class="card-actions">
                    <button class="btn btn-danger btn-remove-student" data-student-id="${student.id}" data-course-id="${courseId}">Remove</button>
                </div>
            </div>
        `);
    }
    
    // Dropdown population functions
    function populateStudentDropdown(students) {
        const dropdown = $('#enrollment-student');
        dropdown.empty().append('<option value="">Select Student</option>');
        
        students.forEach(student => {
            dropdown.append(`<option value="${student.id}">${student.email}</option>`);
        });
    }
    
    function populateCourseDropdown(courses) {
        const dropdown = $('#enrollment-course');
        dropdown.empty().append('<option value="">Select Course</option>');
        
        courses.forEach(course => {
            dropdown.append(`<option value="${course.id}">${course.title}</option>`);
        });
    }
    
    // Course management functions
    function openAddCourseModal() {
        $('#course-modal-title').text('Add Course');
        $('#course-form')[0].reset();
        $('#course-id').val('');
        
        // Clear any current file indicators
        $('.current-file').remove();
        
        openModal('#course-modal');
    }
    
    function handleCourseForm(e) {
        e.preventDefault();
        
        const courseId = $('#course-id').val();
        const isUpdate = courseId !== '';
        const url = isUpdate ? `/api/admin/courses/${courseId}` : '/api/admin/courses';
        const method = isUpdate ? 'PUT' : 'POST';
        
        // Create simple JSON data (no files in basic course creation)
        const courseData = {
            title: $('#course-title').val(),
            description: $('#course-description').val(),
            content: $('#course-content').val(),
            instructor: $('#course-instructor').val(),
            duration: $('#course-duration').val()
        };
        
        showLoading();
        
        $.ajax({
            url: url,
            method: method,
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(courseData),
            success: function(response) {
                hideLoading();
                closeModal('#course-modal');
                showToast(isUpdate ? 'Course updated successfully! Use "Manage Sections" to add content.' : 'Course created successfully! Use "Manage Sections" to add content.', 'success');
                loadAdminCourses();
            },
            error: function(xhr) {
                hideLoading();
                const error = xhr.responseJSON?.detail || 'Failed to save course';
                showToast(error, 'error');
            }
        });
    }
    
    // Event delegation for dynamic elements
    $(document).on('click', '.btn-edit-course', function() {
        const courseId = $(this).data('id');
        editCourse(courseId);
    });
    
    $(document).on('click', '.btn-delete-course', function() {
        const courseId = $(this).data('id');
        if (confirm('Are you sure you want to delete this course?')) {
            deleteCourse(courseId);
        }
    });
    
    $(document).on('click', '.btn-remove-student', function() {
        const studentId = $(this).data('student-id');
        const courseId = $(this).data('course-id');
        if (confirm('Are you sure you want to remove this student from the course?')) {
            removeStudentFromCourse(studentId, courseId);
        }
    });
    
    
    function editCourse(courseId) {
        // Find course data (you might want to store this or make an API call)
        $.ajax({
            url: `/api/courses/${courseId}`,
            method: 'GET',
            success: function(course) {
                $('#course-modal-title').text('Edit Course');
                $('#course-id').val(course.id);
                $('#course-title').val(course.title);
                $('#course-description').val(course.description || '');
                $('#course-content').val(course.content || '');
                $('#course-instructor').val(course.instructor || '');
                $('#course-duration').val(course.duration || '');
                
                // Clear file inputs (can't programmatically set file input values for security)
                $('#course-file').val('');
                $('#course-audio').val('');
                
                // Show current files if they exist
                if (course.file_url) {
                    $('#course-file').after(`<small class="current-file">Current file: <a href="${course.file_url}" target="_blank">View</a></small>`);
                }
                if (course.audio_url) {
                    $('#course-audio').after(`<small class="current-file">Current audio: <a href="${course.audio_url}" target="_blank">Listen</a></small>`);
                }
                
                openModal('#course-modal');
            },
            error: function() {
                showToast('Failed to load course data', 'error');
                openModal('#course-modal');
            },
            error: function() {
                showToast('Failed to load course data', 'error');
            }
        });
    }
    
    function deleteCourse(courseId) {
        showLoading();
        
        $.ajax({
            url: `/api/admin/courses/${courseId}`,
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function() {
                hideLoading();
                showToast('Course deleted successfully!', 'success');
                loadAdminCourses();
            },
            error: function(xhr) {
                hideLoading();
                const error = xhr.responseJSON?.detail || 'Failed to delete course';
                showToast(error, 'error');
            }
        });
    }
    
    // Enrollment functions
    function enrollStudent() {
        const studentId = $('#enrollment-student').val();
        const courseId = $('#enrollment-course').val();
        
        if (!studentId || !courseId) {
            showToast('Please select both student and course', 'warning');
            return;
        }
        
        showLoading();
        
        $.ajax({
            url: '/api/admin/enroll',
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            contentType: 'application/json',
            data: JSON.stringify({ student_id: parseInt(studentId), course_id: parseInt(courseId) }),
            success: function() {
                hideLoading();
                showToast('Student enrolled successfully!', 'success');
                loadCourseStudents();
            },
            error: function(xhr) {
                hideLoading();
                const error = xhr.responseJSON?.detail || 'Failed to enroll student';
                showToast(error, 'error');
            }
        });
    }
    
    function removeEnrollment() {
        const studentId = $('#enrollment-student').val();
        const courseId = $('#enrollment-course').val();
        
        if (!studentId || !courseId) {
            showToast('Please select both student and course', 'warning');
            return;
        }
        
        if (!confirm('Are you sure you want to remove this enrollment?')) {
            return;
        }
        
        removeStudentFromCourse(studentId, courseId);
    }
    
    function removeStudentFromCourse(studentId, courseId) {
        showLoading();
        
        $.ajax({
            url: '/api/admin/enroll',
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
            contentType: 'application/json',
            data: JSON.stringify({ student_id: parseInt(studentId), course_id: parseInt(courseId) }),
            success: function() {
                hideLoading();
                showToast('Student removed from course successfully!', 'success');
                loadCourseStudents();
            },
            error: function(xhr) {
                hideLoading();
                const error = xhr.responseJSON?.detail || 'Failed to remove student from course';
                showToast(error, 'error');
            }
        });
    }
    
    // Section management functionality
    $(document).on('click', '.btn-manage-sections', function() {
        const courseId = $(this).data('id');
        console.log('Manage Sections clicked for course:', courseId);
        showSectionManager(courseId);
    });

    function showSectionManager(courseId) {
        console.log('ShowSectionManager called for courseId:', courseId);
        // Fetch course details first
        $.get(`/api/courses/${courseId}`, function(course) {
            console.log('Course data retrieved:', course);
            // First remove any existing section manager modal
            $('#section-manager-modal').remove();
            
            const modal = $(`
                <div class="modal" id="section-manager-modal" data-course-id="${courseId}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Manage Sections - ${course.title}</h2>
                            <span class="close">&times;</span>
                        </div>
                        <div class="modal-body">
                            <div class="add-section-form">
                                <h3>Add New Section</h3>
                                <input type="text" id="section-title" placeholder="Section Title" required>
                                <textarea id="section-description" placeholder="Section Description" rows="3"></textarea>
                                <button class="btn btn-primary" onclick="addSection(${courseId})">Add Section</button>
                            </div>
                            <div class="sections-list" id="sections-list">
                                <h3>Existing Sections</h3>
                                <div id="sections-container"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
            
            $('body').append(modal);
            modal.show();
            
            // Explicitly bind close button for this modal
            modal.find('.close').off('click').on('click', function() {
                console.log('Section manager close button clicked');
                closeModal(modal);
            });
            
            // Close modal with Escape key
            $(document).off('keydown.sectionModal').on('keydown.sectionModal', function(e) {
                if (e.key === 'Escape' && $('#section-manager-modal').is(':visible')) {
                    console.log('Escape key pressed, closing section modal');
                    closeModal(modal);
                }
            });
            
            // Close modal when clicking outside
            modal.off('click').on('click', function(e) {
                if (e.target === this) {
                    console.log('Clicked outside modal, closing');
                    closeModal(modal);
                }
            });
            
            console.log('Modal should be visible now');
            loadCourseSections(courseId);
        }).fail(function(xhr) {
            console.error('Failed to load course:', xhr);
        });
    }

    function loadCourseSections(courseId) {
        $.ajax({
            url: `/api/admin/courses/${courseId}/sections`,
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
            success: function(sections) {
                const container = $('#sections-container');
                container.empty();
                
                sections.forEach(section => {
                    const sectionEl = $(`
                        <div class="section-item" data-id="${section.id}">
                            <div class="section-header">
                                <h4>${section.title}</h4>
                                <div class="section-actions">
                                    <button class="btn btn-sm" onclick="showAddDocument(${section.id})">Add Document</button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteSection(${section.id})">Delete</button>
                                </div>
                            </div>
                            <p>${section.description || 'No description'}</p>
                            <div class="section-documents" id="documents-${section.id}"></div>
                        </div>
                    `);
                    container.append(sectionEl);
                    renderSectionDocuments(section.id, section.documents || []);
                });
            },
            error: function(xhr) {
                console.error('Error loading sections:', xhr);
            }
        });
    }
    
    function renderSectionDocuments(sectionId, documents) {
        const container = $(`#documents-${sectionId}`);
        container.empty();
        
        if (documents.length === 0) {
            container.append('<p class="no-documents">No documents uploaded</p>');
            return;
        }
        
        documents.forEach(doc => {
            const icon = doc.file_type === 'audio' ? '🎵' : '📄';
            const docEl = $(`
                <div class="document-item">
                    <a href="#" onclick="previewMedia('${encodeURIComponent(doc.file_url)}', '${encodeURIComponent(doc.title)}', '${doc.file_type}')" class="document-link">
                        ${icon} ${doc.title}
                    </a>
                    <button class="btn btn-sm btn-danger" onclick="deleteDocument(${doc.id})">×</button>
                </div>
            `);
            container.append(docEl);
        });
    }

    window.addSection = function(courseId) {
        const title = $('#section-title').val();
        const description = $('#section-description').val();
        
        if (!title) {
            alert('Section title is required');
            return;
        }
        
        $.ajax({
            url: `/api/admin/courses/${courseId}/sections`,
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({ title, description }),
            success: function() {
                $('#section-title').val('');
                $('#section-description').val('');
                loadCourseSections(courseId);
            },
            error: function(xhr) {
                console.error('Error adding section:', xhr);
                alert('Error adding section: ' + (xhr.responseJSON?.detail || 'Unknown error'));
            }
        });
    };

    window.deleteSection = function(sectionId) {
        if (confirm('Are you sure you want to delete this section and all its documents?')) {
            $.ajax({
                url: `/api/admin/sections/${sectionId}`,
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
                success: function() {
                    $(`.section-item[data-id="${sectionId}"]`).remove();
                },
                error: function(xhr) {
                    console.error('Error deleting section:', xhr);
                    alert('Error deleting section: ' + (xhr.responseJSON?.detail || 'Unknown error'));
                }
            });
        }
    };

    window.showAddDocument = function(sectionId) {
        const form = $(`
            <div class="add-document-form" id="add-doc-form-${sectionId}">
                <input type="text" placeholder="Document Title" id="doc-title-${sectionId}" required>
                <input type="file" id="doc-file-${sectionId}" accept=".pdf,.doc,.docx,.txt,.mp3,.wav,.ogg,.m4a" required>
                <button class="btn btn-sm" onclick="uploadDocument(${sectionId})">Upload</button>
                <button class="btn btn-sm btn-outline" onclick="cancelAddDocument(${sectionId})">Cancel</button>
            </div>
        `);
        
        const container = $(`#documents-${sectionId}`);
        if (container.find('.add-document-form').length === 0) {
            container.append(form);
        }
    };

    window.uploadDocument = function(sectionId) {
        const title = $(`#doc-title-${sectionId}`).val();
        const file = $(`#doc-file-${sectionId}`)[0].files[0];
        
        if (!title || !file) {
            alert('Please provide both title and file');
            return;
        }
        
        const formData = new FormData();
        formData.append('title', title);
        formData.append('file', file);
        
        $.ajax({
            url: `/api/admin/sections/${sectionId}/documents`,
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            data: formData,
            processData: false,
            contentType: false,
            success: function() {
                $(`#add-doc-form-${sectionId}`).remove();
                // Reload the entire section to show the new document
                const courseId = $('#section-manager-modal').data('course-id');
                if (courseId) {
                    loadCourseSections(courseId);
                } else {
                    location.reload(); // Fallback
                }
            },
            error: function(xhr) {
                console.error('Error uploading document:', xhr);
                alert('Error uploading document: ' + (xhr.responseJSON?.detail || 'Unknown error'));
            }
        });
    };

    window.cancelAddDocument = function(sectionId) {
        $(`#add-doc-form-${sectionId}`).remove();
    };

    window.deleteDocument = function(docId) {
        if (confirm('Are you sure you want to delete this document?')) {
            $.ajax({
                url: `/api/admin/documents/${docId}`,
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
                success: function() {
                    // Reload the sections to show updated document list
                    const courseId = $('#section-manager-modal').data('course-id');
                    if (courseId) {
                        loadCourseSections(courseId);
                    } else {
                        location.reload(); // Fallback
                    }
                },
                error: function(xhr) {
                    console.error('Error deleting document:', xhr);
                    alert('Error deleting document: ' + (xhr.responseJSON?.detail || 'Unknown error'));
                }
            });
        }
    };

    // Media Preview Functionality
    window.previewMedia = function(fileUrl, title, fileType) {
        // Decode URI components
        const decodedUrl = decodeURIComponent(fileUrl);
        const decodedTitle = decodeURIComponent(title);
        
        console.log('Preview Media Called:', {
            originalUrl: fileUrl,
            decodedUrl: decodedUrl,
            title: decodedTitle,
            fileType: fileType
        });
        
        const modal = $('#media-preview-modal');
        const mediaContainer = $('#media-container');
        const mediaTitle = $('#media-title');
        const downloadBtn = $('#download-media-btn');
        const loadingDiv = $('#media-loading');
        const errorDiv = $('#media-error');
        
        // Set title and download link
        mediaTitle.text(decodedTitle);
        downloadBtn.off('click').on('click', function() {
            downloadFile(decodedUrl, decodedTitle);
        });
        
        // Clear previous content
        mediaContainer.empty();
        loadingDiv.show();
        errorDiv.hide();
        
        // Show modal
        modal.show();
        
        // Test if URL is accessible
        fetch(decodedUrl, { method: 'HEAD' })
            .then(response => {
                console.log('URL accessible:', response.ok);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                // Determine file type and create appropriate preview
                if (fileType === 'audio' || fileType.startsWith('audio/')) {
                    previewAudio(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                } else if (fileType.startsWith('video/')) {
                    previewVideo(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                } else if (fileType.startsWith('image/')) {
                    previewImage(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                } else if (fileType === 'application/pdf' || decodedUrl.toLowerCase().endsWith('.pdf')) {
                    previewPDF(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                } else if (fileType.includes('text/') || 
                           fileType.includes('application/json') || 
                           fileType.includes('application/xml')) {
                    previewText(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                } else {
                    // For documents, try to determine type from URL extension
                    const url = decodedUrl.toLowerCase();
                    if (url.includes('.pdf') || url.includes('pdf')) {
                        previewPDF(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                    } else if (url.match(/\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|$)/)) {
                        previewImage(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                    } else if (url.match(/\.(mp3|wav|ogg|m4a|aac)(\?|$)/)) {
                        previewAudio(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                    } else if (url.match(/\.(mp4|webm|ogv|avi|mov)(\?|$)/)) {
                        previewVideo(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                    } else if (url.match(/\.(txt|md|json|xml|css|js|html)(\?|$)/)) {
                        previewText(decodedUrl, mediaContainer, loadingDiv, errorDiv);
                    } else {
                        // Unsupported file type
                        loadingDiv.hide();
                        errorDiv.html('This file type cannot be previewed. You can download it using the button above.').show();
                    }
                }
            })
            .catch(error => {
                console.error('URL not accessible:', error);
                loadingDiv.hide();
                errorDiv.html('Failed to load document for preview. You can download it using the button above.').show();
            });
    };
    
    function previewAudio(fileUrl, container, loading, error) {
        loading.hide();
        const audio = $(`
            <div class="audio-preview">
                <div class="audio-info">🎵 Audio File</div>
                <audio controls preload="metadata" style="width: 100%; max-width: 500px;">
                    <source src="${fileUrl}" type="audio/mpeg">
                    <source src="${fileUrl}" type="audio/wav">
                    <source src="${fileUrl}" type="audio/ogg">
                    <source src="${fileUrl}">
                    Your browser does not support audio playback.
                </audio>
                <div class="audio-fallback" style="margin-top: 15px; text-align: center; display: none;">
                    <p>Unable to play audio in browser</p>
                    <a href="${fileUrl}" target="_blank" class="btn btn-primary btn-sm">Open Audio File</a>
                </div>
            </div>
        `);
        container.append(audio);
        
        // Handle audio load error
        const audioElement = audio.find('audio')[0];
        audioElement.onerror = function() {
            console.log('Audio failed to load');
            audio.find('.audio-fallback').show();
        };
        
        // Check if audio loaded successfully after a delay
        setTimeout(() => {
            if (audioElement.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) {
                audio.find('.audio-fallback').show();
            }
        }, 3000);
    }
    
    function previewVideo(fileUrl, container, loading, error) {
        loading.hide();
        const video = $(`
            <video controls preload="metadata">
                <source src="${fileUrl}" type="video/mp4">
                <source src="${fileUrl}" type="video/webm">
                <source src="${fileUrl}" type="video/ogg">
                Your browser does not support video playback.
            </video>
        `);
        container.append(video);
        
        // Handle video load error
        video.on('error', function() {
            error.show();
        });
    }
    
    function previewImage(fileUrl, container, loading, error) {
        const img = $(`<img alt="Image preview" style="max-width: 100%; max-height: 70vh; object-fit: contain;">`);
        
        img.on('load', function() {
            loading.hide();
            container.append(img);
        }).on('error', function() {
            console.log('Image failed to load');
            loading.hide();
            container.append($(`
                <div class="image-fallback" style="text-align: center; padding: 40px;">
                    <p>🖼️ Image Preview</p>
                    <p>Unable to display image</p>
                    <a href="${fileUrl}" target="_blank" class="btn btn-primary">Open Image</a>
                </div>
            `));
        });
        
        img.attr('src', fileUrl);
    }
    
    function previewPDF(fileUrl, container, loading, error) {
        loading.hide();
        
        // Use proxy URL for better PDF inline viewing
        const proxyUrl = `/api/pdf-proxy?url=${encodeURIComponent(fileUrl)}`;
        console.log('Using PDF proxy URL:', proxyUrl);
        const pdfViewer = $(`
            <div class="pdf-preview">
                <div class="pdf-viewer-container">
                    <!-- Try object element first with proxy URL (best compatibility) -->
                    <object id="pdf-object" data="${proxyUrl}#view=FitH&toolbar=1" type="application/pdf" width="100%" height="600px">
                        <!-- Fallback iframe inside object -->
                        <iframe id="pdf-iframe" src="${proxyUrl}" 
                                title="PDF Preview" width="100%" height="600px" style="border: none;">
                        </iframe>
                    </object>
                    
                    <!-- Final fallback with better styling -->
                    <div class="pdf-fallback" style="display: none; padding: 40px; text-align: center; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="font-size: 4em; margin-bottom: 20px; color: #6B46C1;">📄</div>
                        <h3 style="color: #2d3748; margin-bottom: 15px;">PDF Document Ready</h3>
                        <p style="color: #4a5568; margin: 15px 0; line-height: 1.6;">
                            Your browser may not support inline PDF viewing.<br>
                            Choose an option below to access the document.
                        </p>
                        <div style="margin: 25px 0; display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                            <a href="${fileUrl}" target="_blank" class="btn btn-primary" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                🔗 Open in New Tab
                            </a>
                            <button onclick="window.open('${fileUrl}', '_blank')" class="btn btn-outline" style="background: white; color: #667eea; border: 2px solid #667eea; padding: 12px 24px; border-radius: 8px; display: inline-flex; align-items: center; gap: 8px;">
                                � View PDF
                            </button>
                        </div>
                        <div style="margin-top: 20px;">
                            <small style="color: #718096; font-style: italic;">
                                💡 Tip: The "View PDF (Inline)" button should prevent automatic downloads.
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `);
        container.append(pdfViewer);
        
        const pdfObject = pdfViewer.find('#pdf-object');
        const iframe = pdfViewer.find('#pdf-iframe');
        const fallback = pdfViewer.find('.pdf-fallback');
        
        // Check if PDF loads successfully
        let loadCheckTimer = setTimeout(() => {
            // If object/iframe doesn't seem to be working, show fallback
            try {
                // Check if object has loaded content
                const objectEl = pdfObject[0];
                if (!objectEl || objectEl.clientHeight === 0) {
                    console.log('PDF object failed to load, showing fallback options');
                    pdfObject.hide();
                    fallback.show();
                }
            } catch(e) {
                console.log('PDF loading check failed, showing fallback:', e.message);
                pdfObject.hide();
                fallback.show();
            }
        }, 4000);
        
        // Handle object load success
        pdfObject.on('load', function() {
            console.log('PDF object loaded successfully');
            clearTimeout(loadCheckTimer);
        });
        
        // Handle iframe load
        iframe.on('load', function() {
            console.log('PDF iframe loaded');
            clearTimeout(loadCheckTimer);
        });
        
        // Handle errors
        pdfObject.on('error', function() {
            console.log('PDF object error, showing fallback');
            clearTimeout(loadCheckTimer);
            pdfObject.hide();
            fallback.show();
        });
        
        iframe.on('error', function() {
            console.log('PDF iframe error, showing fallback');
            clearTimeout(loadCheckTimer);
            pdfObject.hide();
            fallback.show();
        });
    }
    
    function previewText(fileUrl, container, loading, error) {
        $.ajax({
            url: fileUrl,
            method: 'GET',
            dataType: 'text',
            success: function(data) {
                loading.hide();
                const textPreview = $(`
                    <div class="text-preview">
                        <pre style="white-space: pre-wrap; max-height: 60vh; overflow-y: auto; background: #f5f5f5; padding: 15px; border-radius: 4px;">${escapeHtml(data)}</pre>
                    </div>
                `);
                container.append(textPreview);
            },
            error: function() {
                loading.hide();
                error.show();
            }
        });
    }
    
    function downloadFile(fileUrl, filename) {
        // Create a temporary link element for download
        const link = document.createElement('a');
        link.href = fileUrl;
        link.download = filename;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Download started!', 'success');
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Utility functions
    function openModal(modalId) {
        $(modalId).addClass('show').fadeIn(300);
    }
    
    function closeModal(modalId) {
        let modal;
        
        // Handle both jQuery objects and selectors
        if (typeof modalId === 'string') {
            modal = $(modalId);
        } else {
            modal = modalId;
        }
        
        // Clean up section manager modal specifically
        if (modal.attr('id') === 'section-manager-modal') {
            $(document).off('keydown.sectionModal');
        }
        
        modal.removeClass('show').fadeOut(300, function() {
            // Remove dynamically created modals
            if (modal.attr('id') === 'section-manager-modal') {
                modal.remove();
            }
        });
    }
    
    // Media modal close events
    $(document).on('click', '#media-preview-modal .close', function() {
        closeMediaModal();
    });
    
    $(document).on('click', '#media-preview-modal', function(e) {
        if (e.target === this) {
            closeMediaModal();
        }
    });
    
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape' && $('#media-preview-modal').is(':visible')) {
            closeMediaModal();
        }
    });
    
    function closeMediaModal() {
        const modal = $('#media-preview-modal');
        const mediaContainer = $('#media-container');
        
        // Stop any playing audio/video
        mediaContainer.find('audio, video').each(function() {
            this.pause();
        });
        
        // Clear content
        mediaContainer.empty();
        $('#media-loading').hide();
        $('#media-error').hide();
        
        // Hide modal
        modal.fadeOut(300);
    }
    
    function showLoading() {
        $('#loading').show();
    }
    
    function hideLoading() {
        $('#loading').hide();
    }
    
    function showToast(message, type = 'info', duration = 5000) {
        const toast = $(`
            <div class="toast ${type}">
                ${message}
            </div>
        `);
        
        $('#toast-container').append(toast);
        
        setTimeout(() => {
            toast.fadeOut(300, function() {
                $(this).remove();
            });
        }, duration);
    }
    
    // Utility function for email validation
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});
