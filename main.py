from imports import *

if __name__ == '__main__':
    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create and show the login/signup windows
    signup_window = SignupWindow(None)  # Temporarily pass None as the login window
    login_window = LoginWindow(signup_window)
    signup_window.login_window = login_window  # Now assign the login window to signup_window
    login_window.show()

    # Start the application event loop
    sys.exit(app.exec_())
 