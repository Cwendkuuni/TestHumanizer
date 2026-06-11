@Test(timeout = 4000)
    public void testConstructorWithNullParentFormAndWriteAccess() throws Throwable {
        // Given: A session properties object and null parent form
        SessionProperties sessionProperties = new SessionProperties();
        DisplayableListPanel displayableListPanel = null;

        // When: Initializing DisplayableListPanel with null parent form and write access
        // Then: Expect a NullPointerException
        try {
            displayableListPanel = new DisplayableListPanel(sessionProperties, null, "startupOptions", true, true);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Verify exception source
            verifyException("macaw.util.DisplayableListPanel", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithNullParentFormWithoutWriteAccess() throws Throwable {
        // Given: A session properties object and null parent form
        SessionProperties sessionProperties = new SessionProperties();
        DisplayableListPanel displayableListPanel = null;

        // When: Initializing DisplayableListPanel with null parent form without write access
        // Then: Expect a NullPointerException
        try {
            displayableListPanel = new DisplayableListPanel(sessionProperties, null, "database", true);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Verify exception source
            verifyException("macaw.util.DisplayableListPanel", e);
        }
    }