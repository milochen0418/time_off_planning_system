# Leave Booking Management System (預約休假管理系統)

## Phase 1: Authentication & Database Models ✅
- [x] Create database models for User and LeaveBooking
- [x] Implement user registration and login/logout functionality
- [x] Build login and registration pages with form validation
- [x] Set up session management with protected routes

## Phase 2: Personal Leave Management ✅
- [x] Build the "My Leaves" page with a list of all booked leaves
- [x] Implement add new leave booking form (date, start time, end time)
- [x] Implement edit and delete functionality for each leave item
- [x] Add form validation (date/time checks, conflict detection)

## Phase 3: Shared Calendar View ✅
- [x] Build the Calendar page with month/week/day view toggle
- [x] Implement month view showing all users' leaves per day
- [x] Implement week view with 7-day horizontal axis and time vertical axis
- [x] Implement day view showing detailed hourly schedule for one day
- [x] Navigation controls for prev/next period and "today" button

## Phase 4: Super Admin Login & User Management ✅
- [x] Add "超級管理者" link on the login page that goes to /admin-login
- [x] Build admin login page with default credentials (admin / admin)
- [x] Create AdminState with admin session management, admin_logged_in, admin user CRUD
- [x] Build admin dashboard with "User Management" tab - add, edit, delete users (username, password, display_name)
- [x] Protect admin routes with admin auth check

## Phase 5: Message Board & Contact Form ✅
- [x] Replace "點此註冊" on login page with "留言給超級管理者" link going to /contact
- [x] Build contact form page with fields: 員工編號, 姓名, 信箱, 通訊軟體方式 (Line/WhatsApp/Phone dropdown + value), message (multiline), auto-capture submission timestamp
- [x] Create MessageState for storing messages with timestamps
- [x] Add "Message Board" tab in admin dashboard showing all messages with sender info, timestamp, and contact details
- [x] Allow admin to view and delete messages from the board
