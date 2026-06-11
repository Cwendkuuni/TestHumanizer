@Test(timeout = 4000)
    public void testConstructorWithNullAttributes() throws Throwable {
        // Given: A null FollowAppAttributes object
        TabbedPane tabbedPane = null;

        // When: Attempting to create a TabbedPane with null attributes
        try {
            tabbedPane = new TabbedPane((FollowAppAttributes) null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Then: A NullPointerException is expected
            // Verify that the exception is thrown from the TabbedPane class
            verifyException("ghm.follow.gui.TabbedPane", e);
        }
    }