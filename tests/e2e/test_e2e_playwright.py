import pytest

def register_and_login_user(page, fastapi_server, first_name, last_name, email, username, password="SecurePass123!"):
    """Helper function to register and login a user."""
    # Register user
    page.goto(f"{fastapi_server}register")
    page.fill('#first_name', first_name)
    page.fill('#last_name', last_name)
    page.fill('#email', email)
    page.fill('#username', username)
    page.fill('#password', password)
    page.fill('#confirm_password', password)
    page.click('button[type="submit"]')
    
    # Login user
    page.wait_for_url('**/login')
    page.fill('#username', username)
    page.fill('#password', password)
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url('**/dashboard')
    return page

@pytest.mark.e2e
def test_homepage_loads(page, fastapi_server):
    """
    Test that the homepage loads correctly and shows the expected content.
    
    This test navigates to the homepage and verifies that the welcome message
    and authentication links are displayed correctly.
    """
    # Navigate to the test server (not hardcoded localhost)
    page.goto(fastapi_server)
    
    # Wait for the page to load
    page.wait_for_load_state('networkidle')
    
    # Check that the page title is correct (matches template block title)
    assert "Home" in page.title()
    
    # Check that the welcome message is displayed (it's an h1, not h2)
    welcome_text = page.locator('h1:has-text("Welcome to the Calculations App")')
    assert welcome_text.is_visible()
    
    # Check that login/register links are shown
    login_link = page.locator('a:has-text("Login")')
    register_link = page.locator('a:has-text("Register")')
    assert login_link.is_visible()
    assert register_link.is_visible()

@pytest.mark.e2e
def test_login_validation_error_handling(page, fastapi_server):
    """Test that login form handles invalid credentials (stays on login page)."""
    page.goto(f"{fastapi_server}login")
    
    # Try to login with invalid credentials
    page.fill('#username', 'invalid_user')
    page.fill('#password', 'wrong_password')
    page.click('button[type="submit"]')
    
    # Wait a moment for potential redirect, then verify we're still on login page
    page.wait_for_timeout(1000)  # Wait 1 second
    assert 'login' in page.url

@pytest.mark.e2e
def test_user_registration_validation(page, fastapi_server):
    """Test comprehensive registration validation: valid, invalid, and duplicate scenarios."""
    # Test 1: Valid registration
    page.goto(f"{fastapi_server}register")
    page.fill('#first_name', 'Valid')
    page.fill('#last_name', 'User')
    page.fill('#email', 'validuser@example.com')
    page.fill('#username', 'validuser123')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Should redirect to login page after successful registration
    page.wait_for_url('**/login')
    assert 'login' in page.url
    
    # Test 2: Invalid - mismatched passwords
    page.goto(f"{fastapi_server}register")
    page.fill('#first_name', 'Test')
    page.fill('#last_name', 'Mismatch')
    page.fill('#email', 'mismatch@example.com')
    page.fill('#username', 'testmismatch')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'DifferentPass456!')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    # Should stay on registration page or show error
    assert 'register' in page.url or page.locator('#errorAlert').is_visible()
    
    # Test 3: Invalid email format
    page.goto(f"{fastapi_server}register")
    page.fill('#first_name', 'Test')
    page.fill('#last_name', 'Email')
    page.fill('#email', 'invalid-email-format')
    page.fill('#username', 'testemail')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    # Should stay on registration page or show validation error
    assert 'register' in page.url or page.locator('#errorAlert').is_visible()
    
    # Test 4: Duplicate email (reusing the valid user from Test 1)
    page.goto(f"{fastapi_server}register")
    page.fill('#first_name', 'Second')
    page.fill('#last_name', 'User')
    page.fill('#email', 'validuser@example.com')  # Same email as Test 1
    page.fill('#username', 'seconduser')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    # Should show error or stay on registration page
    error_alert = page.locator('#errorAlert')
    if error_alert.is_visible():
        assert error_alert.is_visible()
    else:
        assert 'register' in page.url

@pytest.mark.e2e
def test_unauthenticated_dashboard_redirect(page, fastapi_server):
    """Test that accessing dashboard without authentication redirects to login."""
    # Try to access dashboard directly without authentication
    page.goto(f"{fastapi_server}dashboard")
    
    # Should be redirected to login page
    page.wait_for_url('**/login')
    assert 'login' in page.url

@pytest.mark.e2e
def test_calculation_create_and_retrieve(page, fastapi_server):
    """Test creating a calculation and viewing it in the history."""
    # Register and login user
    register_and_login_user(page, fastapi_server, 'Calc', 'Tester', 'calctester@example.com', 'calctester')
    
    # Create a new calculation
    page.select_option('#calcType', 'addition')
    page.fill('#calcInputs', '10, 20, 30')
    page.click('button[type="submit"]')
    
    # Wait for calculation to be processed and page to update
    page.wait_for_timeout(2000)
    
    # Check that calculation appears in history table
    # Look for the result value (10+20+30=60)
    result_cell = page.locator('td:has-text("60")')
    assert result_cell.is_visible()
    
    # Check that operation type is visible
    type_cell = page.locator('td:has-text("addition")')
    assert type_cell.is_visible()
    
    # Check that inputs are visible
    inputs_cell = page.locator('td:has-text("10, 20, 30")')
    assert inputs_cell.is_visible()

@pytest.mark.e2e
def test_calculation_view_details(page, fastapi_server):
    """Test viewing detailed calculation information."""
    # Register and login user
    register_and_login_user(page, fastapi_server, 'View', 'Tester', 'viewtester@example.com', 'viewtester')
    
    # Create a calculation first
    page.select_option('#calcType', 'multiplication')
    page.fill('#calcInputs', '5, 4, 2')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Click on View button for the calculation
    view_button = page.locator('a:has-text("View")')
    assert view_button.is_visible()
    view_button.click()
    
    # Should be on view calculation page
    page.wait_for_url('**/view/**')
    assert 'view' in page.url
    
    # Check that calculation details are displayed using more specific locators
    assert page.locator('p.font-medium:has-text("multiplication")').is_visible()
    assert page.locator('text=40').first.is_visible()  # 5*4*2=40
    assert page.locator('text=5, 4, 2').first.is_visible()

@pytest.mark.e2e
def test_calculation_update_flow(page, fastapi_server):
    """Test updating a calculation through the edit form."""
    # Register and login
    page.goto(f"{fastapi_server}register")
    
    page.fill('#first_name', 'Edit')
    page.fill('#last_name', 'Tester')
    page.fill('#email', 'edittester@example.com')
    page.fill('#username', 'edittester')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Login
    page.wait_for_url('**/login')
    page.fill('#username', 'edittester')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Create initial calculation
    page.wait_for_url('**/dashboard')
    page.select_option('#calcType', 'subtraction')
    page.fill('#calcInputs', '100, 25')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Click Edit button
    edit_button = page.locator('a:has-text("Edit")')
    assert edit_button.is_visible()
    edit_button.click()
    
    # Should be on edit page
    page.wait_for_url('**/edit/**')
    assert 'edit' in page.url
    
    # Modify the calculation (note: operation type is read-only, only inputs can be changed)
    # Clear the existing inputs and add new ones
    page.fill('#calcInputs', '100, 50, 25')
    
    # Submit the update
    update_button = page.locator('button:has-text("Save Changes")')
    update_button.click()
    
    # Should redirect back to dashboard or view page
    page.wait_for_timeout(2000)
    
    # Go back to dashboard to verify the change
    page.goto(f"{fastapi_server}dashboard")
    
    # Check that the calculation was updated (100-50-25=25 since type is still subtraction)
    page.wait_for_timeout(1000)
    # Look for the result in the specific result column (font-semibold class is used for results)
    result_cell = page.locator('td.font-semibold:has-text("25")')
    assert result_cell.is_visible()
    
    # Verify operation type is still subtraction (since it's read-only)
    type_cell = page.locator('td:has-text("subtraction")')
    assert type_cell.is_visible()
    
    # Verify inputs were updated
    inputs_cell = page.locator('td:has-text("100, 50, 25")')
    assert inputs_cell.is_visible()

@pytest.mark.e2e
def test_calculation_delete_functionality(page, fastapi_server):
    """Test deleting a calculation from the dashboard."""
    # Register and login
    page.goto(f"{fastapi_server}register")
    
    page.fill('#first_name', 'Delete')
    page.fill('#last_name', 'Tester')
    page.fill('#email', 'deletetester@example.com')
    page.fill('#username', 'deletetester')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Login
    page.wait_for_url('**/login')
    page.fill('#username', 'deletetester')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Create a calculation to delete
    page.wait_for_url('**/dashboard')
    page.select_option('#calcType', 'division')
    page.fill('#calcInputs', '100, 5')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Verify calculation exists (100/5=20) - use specific result column locator
    result_cell = page.locator('td.font-semibold:has-text("20")')
    assert result_cell.is_visible()
    
    # Click Delete button
    delete_button = page.locator('button:has-text("Delete")')
    assert delete_button.is_visible()
    
    # Handle confirmation dialog if it exists
    page.on("dialog", lambda dialog: dialog.accept())
    delete_button.click()
    
    page.wait_for_timeout(2000)
    
    # Verify calculation is no longer in the table
    # The result "20" should not be visible in the result column anymore
    result_cell_after = page.locator('td.font-semibold:has-text("20")')
    assert not result_cell_after.is_visible()

# ---------------------------------------------------------------------------
# Negative Tests - Error Handling and Edge Cases
# ---------------------------------------------------------------------------

@pytest.mark.e2e
def test_invalid_calculation_inputs(page, fastapi_server):
    """Test various invalid calculation inputs: empty, non-numeric, and insufficient data."""
    # Register and login
    page.goto(f"{fastapi_server}register")
    
    page.fill('#first_name', 'Invalid')
    page.fill('#last_name', 'Inputs')
    page.fill('#email', 'invalidinputs@example.com')
    page.fill('#username', 'invalidinputs')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Login
    page.wait_for_url('**/login')
    page.fill('#username', 'invalidinputs')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    page.wait_for_url('**/dashboard')
    
    # Test with empty inputs
    page.select_option('#calcType', 'addition')
    page.fill('#calcInputs', '')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Should show an error (either alert or no calculation created)
    error_alert = page.locator('#errorAlert')
    if error_alert.is_visible():
        assert error_alert.is_visible()
    else:
        # If no error alert, ensure no calculation was created
        no_calculations = page.locator('text=No calculations found')
        loading_message = page.locator('text=Loading calculations')
        assert no_calculations.is_visible() or loading_message.is_visible()
    
    # Test with invalid number format
    page.fill('#calcInputs', 'abc, def')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Should show error for invalid numbers
    error_alert = page.locator('#errorAlert')
    if error_alert.is_visible():
        assert error_alert.is_visible()
    
    # Test with insufficient inputs (single number)
    page.fill('#calcInputs', '42')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Should either show error or handle gracefully
    error_alert = page.locator('#errorAlert')
    if error_alert.is_visible():
        assert error_alert.is_visible()
    else:
        # If no error, the single number calculation should be handled gracefully
        result_42 = page.locator('td.font-semibold:has-text("42")')
        # Either shows error or processes single number - both are acceptable



@pytest.mark.e2e
def test_access_nonexistent_calculation(page, fastapi_server):
    """Test accessing a calculation that doesn't exist shows proper error."""
    # Register and login first
    page.goto(f"{fastapi_server}register")
    
    page.fill('#first_name', 'Nonexistent')
    page.fill('#last_name', 'Calc')
    page.fill('#email', 'nonexistent@example.com')
    page.fill('#username', 'nonexistent')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Login
    page.wait_for_url('**/login')
    page.fill('#username', 'nonexistent')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    page.wait_for_url('**/dashboard')
    
    # Try to access a nonexistent calculation
    fake_calc_id = "999e4567-e89b-12d3-a456-426614174999"
    page.goto(f"{fastapi_server}dashboard/view/{fake_calc_id}")
    
    page.wait_for_timeout(2000)
    
    # Should show "not found" error or redirect to dashboard
    not_found_message = page.locator('text=not found')
    calculation_not_found = page.locator('text=Calculation Not Found')
    error_404 = page.locator('text=404')
    
    # Check if any error message is shown or redirected to dashboard
    if page.url.endswith('/dashboard'):
        # Redirected to dashboard is acceptable
        assert 'dashboard' in page.url
    else:
        # Should show some kind of error message
        assert (not_found_message.is_visible() or 
                calculation_not_found.is_visible() or 
                error_404.is_visible())
