@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      LinkedList<Object> linkedList0 = new LinkedList<Object>();
      linkedList0.add((Object) null);
      FinalMockCandidateFilter finalMockCandidateFilter0 = new FinalMockCandidateFilter();
      TypeBasedCandidateFilter typeBasedCandidateFilter0 = new TypeBasedCandidateFilter(finalMockCandidateFilter0);
      // Undeclared exception!
      try { 
        typeBasedCandidateFilter0.filterCandidate(linkedList0, (Field) null, (Object) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.mockito.internal.configuration.injection.filter.TypeBasedCandidateFilter", e);
      }
  }

  @Test(timeout = 4000)
  public void test1()  throws Throwable  {
      LinkedList<Object> linkedList0 = new LinkedList<Object>();
      FinalMockCandidateFilter finalMockCandidateFilter0 = new FinalMockCandidateFilter();
      TypeBasedCandidateFilter typeBasedCandidateFilter0 = new TypeBasedCandidateFilter(finalMockCandidateFilter0);
      OngoingInjecter ongoingInjecter0 = typeBasedCandidateFilter0.filterCandidate(linkedList0, (Field) null, (Object) null);
      assertNotNull(ongoingInjecter0);
  }