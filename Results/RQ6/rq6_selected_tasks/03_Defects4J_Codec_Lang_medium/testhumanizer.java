@Test(timeout = 4000)
    public void testClassLoadingThrowsNoClassDefFoundError() throws Throwable {
        // Given: A fully qualified class name that is expected to be missing
        String missingClassName = "org.apache.commons.codec.language.bm.Lang";
        Thread currentThread = Thread.currentThread();
        ClassLoader contextClassLoader = currentThread.getContextClassLoader();
        boolean initialize = true;

        // When: Attempting to load the class using the current thread's context class loader
        // Then: Expect a NoClassDefFoundError to be thrown
        try {
            Class.forName(missingClassName, initialize, contextClassLoader);
            fail("Expecting exception: NoClassDefFoundError");
        } catch (NoClassDefFoundError e) {
            // Expected exception
        }
    }