@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.IS_NULL;
      Predicate<Class<Locale.Category>> predicate0 = predicates_ObjectPredicate0.withNarrowedType();
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      Predicate<CharMatcher> predicate0 = Predicates.isNull();
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      ArrayDeque<Class<CharMatcher>> arrayDeque0 = new ArrayDeque<Class<CharMatcher>>();
      List<Class<CharMatcher>> list0 = Predicates.defensiveCopy((Iterable<Class<CharMatcher>>) arrayDeque0);
      assertTrue(list0.isEmpty());
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      Stack<CharMatcher> stack0 = new Stack<CharMatcher>();
      Predicate<CharMatcher> predicate0 = Predicates.in((Collection<? extends CharMatcher>) stack0);
      Converter<CharMatcher, CharMatcher> converter0 = Converter.identity();
      Predicate<CharMatcher> predicate1 = Predicates.compose(predicate0, (Function<CharMatcher, ? extends CharMatcher>) converter0);
      assertFalse(predicate1.equals((Object)predicate0));
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      LinkedHashSet<Predicates.ObjectPredicate> linkedHashSet0 = new LinkedHashSet<Predicates.ObjectPredicate>();
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.ALWAYS_TRUE;
      linkedHashSet0.add(predicates_ObjectPredicate0);
      Predicate<Predicates.ObjectPredicate> predicate0 = Predicates.and((Iterable<? extends Predicate<? super Predicates.ObjectPredicate>>) linkedHashSet0);
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      LinkedHashSet<Predicates.ObjectPredicate> linkedHashSet0 = new LinkedHashSet<Predicates.ObjectPredicate>();
      Predicate<Predicates.ObjectPredicate> predicate0 = Predicates.in((Collection<? extends Predicates.ObjectPredicate>) linkedHashSet0);
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.ALWAYS_TRUE;
      linkedHashSet0.add(predicates_ObjectPredicate0);
      boolean boolean0 = linkedHashSet0.contains(predicate0);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.NOT_NULL;
      Object object0 = new Object();
      boolean boolean0 = predicates_ObjectPredicate0.apply(object0);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.NOT_NULL;
      boolean boolean0 = predicates_ObjectPredicate0.apply((Object) null);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.IS_NULL;
      boolean boolean0 = predicates_ObjectPredicate0.apply((Object) null);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.IS_NULL;
      boolean boolean0 = predicates_ObjectPredicate0.apply(predicates_ObjectPredicate0);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.IS_NULL;
      Predicate<Predicates.ObjectPredicate> predicate0 = Predicates.equalTo(predicates_ObjectPredicate0);
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.ALWAYS_FALSE;
      CharMatcher charMatcher0 = CharMatcher.forPredicate(predicates_ObjectPredicate0);
      assertNotNull(charMatcher0);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.ALWAYS_FALSE;
      Object object0 = new Object();
      boolean boolean0 = predicates_ObjectPredicate0.apply(object0);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.ALWAYS_TRUE;
      CharMatcher charMatcher0 = CharMatcher.forPredicate(predicates_ObjectPredicate0);
      assertNotNull(charMatcher0);
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.ALWAYS_TRUE;
      Object object0 = new Object();
      boolean boolean0 = predicates_ObjectPredicate0.apply(object0);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.IS_NULL;
      Predicate<Object> predicate0 = Predicates.notNull();
      Predicate<Object> predicate1 = Predicates.or((Predicate<? super Object>) predicates_ObjectPredicate0, (Predicate<? super Object>) predicate0);
      CharMatcher charMatcher0 = CharMatcher.forPredicate(predicate1);
      assertNotNull(charMatcher0);
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      Pattern pattern0 = Pattern.compile("OJM+-4");
      Predicate<CharSequence> predicate0 = Predicates.contains(pattern0);
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      LinkedHashSet<Predicates.ObjectPredicate> linkedHashSet0 = new LinkedHashSet<Predicates.ObjectPredicate>();
      Predicate<Predicates.ObjectPredicate> predicate0 = Predicates.or((Iterable<? extends Predicate<? super Predicates.ObjectPredicate>>) linkedHashSet0);
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      Class<Locale.FilteringMode> class0 = Locale.FilteringMode.class;
      Predicate<Object> predicate0 = Predicates.instanceOf(class0);
      Predicate<Locale.FilteringMode> predicate1 = Predicates.alwaysTrue();
      Predicate<Locale.FilteringMode> predicate2 = Predicates.and((Predicate<? super Locale.FilteringMode>) predicate1, (Predicate<? super Locale.FilteringMode>) predicate0);
      assertFalse(predicate2.equals((Object)predicate1));
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      Predicate<CharMatcher> predicate0 = Predicates.equalTo((CharMatcher) null);
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test20()  throws Throwable  {
      Predicate<Object>[] predicateArray0 = (Predicate<Object>[]) Array.newInstance(Predicate.class, 2);
      // Undeclared exception!
      try { 
        Predicates.or((Predicate<? super Object>[]) predicateArray0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.base.Preconditions", e);
      }
  }

  @Test(timeout = 4000)
  public void test21()  throws Throwable  {
      Predicate<CharMatcher>[] predicateArray0 = (Predicate<CharMatcher>[]) Array.newInstance(Predicate.class, 7);
      // Undeclared exception!
      try { 
        Predicates.and((Predicate<? super CharMatcher>[]) predicateArray0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.base.Preconditions", e);
      }
  }

  @Test(timeout = 4000)
  public void test22()  throws Throwable  {
      Class<CharMatcher> class0 = CharMatcher.class;
      Predicate<Object> predicate0 = Predicates.instanceOf(class0);
      Predicate<CharMatcher> predicate1 = Predicates.or((Predicate<? super CharMatcher>) predicate0, (Predicate<? super CharMatcher>) predicate0);
      Predicate<CharMatcher> predicate2 = Predicates.not(predicate1);
      assertFalse(predicate2.equals((Object)predicate1));
  }

  @Test(timeout = 4000)
  public void test23()  throws Throwable  {
      Predicate<CharSequence> predicate0 = Predicates.containsPattern("#q");
      LinkedHashSet<Predicates.ObjectPredicate> linkedHashSet0 = new LinkedHashSet<Predicates.ObjectPredicate>();
      boolean boolean0 = linkedHashSet0.contains(predicate0);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test24()  throws Throwable  {
      Class<Locale.FilteringMode> class0 = Locale.FilteringMode.class;
      Predicate<Class<?>> predicate0 = Predicates.assignableFrom(class0);
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test25()  throws Throwable  {
      Predicate<Locale.Category> predicate0 = Predicates.alwaysFalse();
      assertNotNull(predicate0);
  }

  @Test(timeout = 4000)
  public void test26()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.IS_NULL;
      CharMatcher charMatcher0 = CharMatcher.forPredicate(predicates_ObjectPredicate0);
      assertNotNull(charMatcher0);
  }

  @Test(timeout = 4000)
  public void test27()  throws Throwable  {
      LinkedHashSet<Predicates.ObjectPredicate> linkedHashSet0 = new LinkedHashSet<Predicates.ObjectPredicate>();
      Class<CharMatcher> class0 = CharMatcher.class;
      Predicate<Object> predicate0 = Predicates.instanceOf(class0);
      boolean boolean0 = linkedHashSet0.contains(predicate0);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test28()  throws Throwable  {
      Predicates.ObjectPredicate predicates_ObjectPredicate0 = Predicates.ObjectPredicate.NOT_NULL;
      CharMatcher charMatcher0 = CharMatcher.forPredicate(predicates_ObjectPredicate0);
      assertNotNull(charMatcher0);
  }

  @Test(timeout = 4000)
  public void test29()  throws Throwable  {
      LinkedHashSet<Predicates.ObjectPredicate> linkedHashSet0 = new LinkedHashSet<Predicates.ObjectPredicate>();
      Predicate<Predicates.ObjectPredicate> predicate0 = Predicates.and((Iterable<? extends Predicate<? super Predicates.ObjectPredicate>>) linkedHashSet0);
      boolean boolean0 = linkedHashSet0.contains(predicate0);
      assertFalse(boolean0);
  }