// Test to verify that the Verifier object correctly stores and retrieves an empty string
    @Test(timeout = 4000)
    public void testVerifierWithEmptyString() throws Throwable {
        // Given: A Verifier object is created with an empty string
        Verifier verifier = new Verifier("");

        // When: The value is retrieved from the Verifier object
        String retrievedValue = verifier.getValue();

        // Then: The retrieved value should be an empty string
        assertEquals("Verifier should return an empty string when initialized with an empty string", "", retrievedValue);
    }