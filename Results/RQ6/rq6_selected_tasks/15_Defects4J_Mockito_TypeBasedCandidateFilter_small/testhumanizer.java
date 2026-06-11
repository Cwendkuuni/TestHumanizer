@Test(timeout = 4000)
    public void testFilterCandidateWithNullFieldAndMocks() throws Throwable {
        // Given: A TypeBasedCandidateFilter with no next filter and a list containing a null object
        TypeBasedCandidateFilter typeBasedCandidateFilter = new TypeBasedCandidateFilter((MockCandidateFilter) null);
        LinkedList<Object> mocks = new LinkedList<>();
        mocks.add(null);

        // When: filterCandidate is called with null field and field instance
        // Then: A NullPointerException is expected
        try {
            typeBasedCandidateFilter.filterCandidate(mocks, (Field) null, (Object) null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Verify: Exception is thrown from TypeBasedCandidateFilter
            verifyException("org.mockito.internal.configuration.injection.filter.TypeBasedCandidateFilter", e);
        }
    }

    @Test(timeout = 4000)
    public void testFilterCandidateWithEmptyMocksAndNullField() throws Throwable {
        // Given: A TypeBasedCandidateFilter with no next filter and an empty list of mocks
        TypeBasedCandidateFilter typeBasedCandidateFilter = new TypeBasedCandidateFilter((MockCandidateFilter) null);
        LinkedList<Object> mocks = new LinkedList<>();

        // When: filterCandidate is called with null field and field instance
        // Then: A NullPointerException is expected
        try {
            typeBasedCandidateFilter.filterCandidate(mocks, (Field) null, (Object) null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Verify: Exception is thrown from TypeBasedCandidateFilter
            verifyException("org.mockito.internal.configuration.injection.filter.TypeBasedCandidateFilter", e);
        }
    }