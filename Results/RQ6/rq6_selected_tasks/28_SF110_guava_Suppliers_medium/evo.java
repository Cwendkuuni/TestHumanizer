@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      Locale.Category locale_Category0 = Locale.Category.DISPLAY;
      Supplier<Locale.Category> supplier0 = Suppliers.ofInstance(locale_Category0);
      TimeUnit timeUnit0 = TimeUnit.MICROSECONDS;
      Suppliers.ExpiringMemoizingSupplier<Locale.Category> suppliers_ExpiringMemoizingSupplier0 = new Suppliers.ExpiringMemoizingSupplier<Locale.Category>(supplier0, 1192L, timeUnit0);
      String string0 = suppliers_ExpiringMemoizingSupplier0.toString();
      assertEquals("Suppliers.memoizeWithExpiration(Suppliers.ofInstance(DISPLAY), 1192000, NANOS)", string0);
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      TimeUnit timeUnit0 = TimeUnit.SECONDS;
      Suppliers.MemoizingSupplier<Locale.Category> suppliers_MemoizingSupplier0 = new Suppliers.MemoizingSupplier<Locale.Category>((Supplier<Locale.Category>) null);
      Supplier<Locale.Category> supplier0 = Suppliers.synchronizedSupplier((Supplier<Locale.Category>) suppliers_MemoizingSupplier0);
      Suppliers.ExpiringMemoizingSupplier<Locale.Category> suppliers_ExpiringMemoizingSupplier0 = new Suppliers.ExpiringMemoizingSupplier<Locale.Category>(supplier0, 1859L, timeUnit0);
      // Undeclared exception!
      try { 
        suppliers_ExpiringMemoizingSupplier0.get();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.base.Suppliers$MemoizingSupplier", e);
      }
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      Locale.Category locale_Category0 = Locale.Category.DISPLAY;
      Supplier<Locale.Category> supplier0 = Suppliers.ofInstance(locale_Category0);
      TimeUnit timeUnit0 = TimeUnit.MICROSECONDS;
      Suppliers.ExpiringMemoizingSupplier<Locale.Category> suppliers_ExpiringMemoizingSupplier0 = new Suppliers.ExpiringMemoizingSupplier<Locale.Category>(supplier0, 1L, timeUnit0);
      System.setCurrentTimeMillis((-1L));
      Locale.Category locale_Category1 = suppliers_ExpiringMemoizingSupplier0.get();
      assertSame(locale_Category1, locale_Category0);
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      Locale.Category locale_Category0 = Locale.Category.FORMAT;
      Supplier<Locale.Category> supplier0 = Suppliers.ofInstance(locale_Category0);
      TimeUnit timeUnit0 = TimeUnit.SECONDS;
      Suppliers.ExpiringMemoizingSupplier<Locale.Category> suppliers_ExpiringMemoizingSupplier0 = new Suppliers.ExpiringMemoizingSupplier<Locale.Category>(supplier0, 1473L, timeUnit0);
      suppliers_ExpiringMemoizingSupplier0.expirationNanos = 1473L;
      Locale.Category locale_Category1 = suppliers_ExpiringMemoizingSupplier0.get();
      assertEquals(Locale.Category.FORMAT, locale_Category1);
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      Supplier<Integer> supplier0 = Suppliers.ofInstance((Integer) null);
      Suppliers.MemoizingSupplier<Integer> suppliers_MemoizingSupplier0 = new Suppliers.MemoizingSupplier<Integer>(supplier0);
      TimeUnit timeUnit0 = TimeUnit.SECONDS;
      Suppliers.ExpiringMemoizingSupplier<Integer> suppliers_ExpiringMemoizingSupplier0 = new Suppliers.ExpiringMemoizingSupplier<Integer>(suppliers_MemoizingSupplier0, 1859L, timeUnit0);
      suppliers_ExpiringMemoizingSupplier0.get();
      Integer integer0 = suppliers_ExpiringMemoizingSupplier0.get();
      assertNull(integer0);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      Integer integer0 = new Integer(2147471940);
      Supplier<Integer> supplier0 = Suppliers.ofInstance(integer0);
      TimeUnit timeUnit0 = TimeUnit.MICROSECONDS;
      Suppliers.ExpiringMemoizingSupplier<Integer> suppliers_ExpiringMemoizingSupplier0 = null;
      try {
        suppliers_ExpiringMemoizingSupplier0 = new Suppliers.ExpiringMemoizingSupplier<Integer>(supplier0, (-248L), timeUnit0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("com.google.common.base.Preconditions", e);
      }
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      Suppliers.MemoizingSupplier<Integer> suppliers_MemoizingSupplier0 = new Suppliers.MemoizingSupplier<Integer>((Supplier<Integer>) null);
      suppliers_MemoizingSupplier0.initialized = true;
      Integer integer0 = suppliers_MemoizingSupplier0.get();
      assertNull(integer0);
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      Suppliers.MemoizingSupplier<Integer> suppliers_MemoizingSupplier0 = new Suppliers.MemoizingSupplier<Integer>((Supplier<Integer>) null);
      Supplier<Integer> supplier0 = Suppliers.memoize((Supplier<Integer>) suppliers_MemoizingSupplier0);
      assertNotNull(supplier0);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      Supplier<Integer> supplier0 = Suppliers.ofInstance((Integer) null);
      Supplier<Integer> supplier1 = Suppliers.synchronizedSupplier(supplier0);
      TimeUnit timeUnit0 = TimeUnit.SECONDS;
      Supplier<Integer> supplier2 = Suppliers.memoizeWithExpiration(supplier1, 1835L, timeUnit0);
      Suppliers.MemoizingSupplier<Integer> suppliers_MemoizingSupplier0 = new Suppliers.MemoizingSupplier<Integer>(supplier2);
      String string0 = suppliers_MemoizingSupplier0.toString();
      assertEquals("Suppliers.memoize(Suppliers.memoizeWithExpiration(Suppliers.synchronizedSupplier(Suppliers.ofInstance(null)), 1835000000000, NANOS))", string0);
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      Converter<Integer, Integer> converter0 = Converter.identity();
      Supplier<Integer> supplier0 = Suppliers.ofInstance((Integer) null);
      TimeUnit timeUnit0 = TimeUnit.MICROSECONDS;
      Supplier<Integer> supplier1 = Suppliers.compose((Function<? super Integer, Integer>) converter0, supplier0);
      Suppliers.ExpiringMemoizingSupplier<Integer> suppliers_ExpiringMemoizingSupplier0 = new Suppliers.ExpiringMemoizingSupplier<Integer>(supplier1, 2088L, timeUnit0);
      Integer integer0 = suppliers_ExpiringMemoizingSupplier0.get();
      assertNull(integer0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      Converter<Locale.Category, Locale.Category> converter0 = Converter.identity();
      Locale.Category locale_Category0 = Locale.Category.DISPLAY;
      Supplier<Locale.Category> supplier0 = Suppliers.ofInstance(locale_Category0);
      Supplier<Locale.Category> supplier1 = Suppliers.compose((Function<? super Locale.Category, Locale.Category>) converter0, supplier0);
      Suppliers.MemoizingSupplier<Locale.Category> suppliers_MemoizingSupplier0 = new Suppliers.MemoizingSupplier<Locale.Category>(supplier1);
      String string0 = suppliers_MemoizingSupplier0.toString();
      assertEquals("Suppliers.memoize(Suppliers.compose(Converter.identity(), Suppliers.ofInstance(DISPLAY)))", string0);
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      Function<Supplier<Integer>, Integer> function0 = Suppliers.supplierFunction();
      assertNotNull(function0);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      Suppliers.MemoizingSupplier<Locale.Category> suppliers_MemoizingSupplier0 = new Suppliers.MemoizingSupplier<Locale.Category>((Supplier<Locale.Category>) null);
      Supplier<Locale.Category> supplier0 = Suppliers.synchronizedSupplier((Supplier<Locale.Category>) suppliers_MemoizingSupplier0);
      Supplier<Locale.Category> supplier1 = Suppliers.memoize(supplier0);
      assertFalse(supplier1.equals((Object)supplier0));
  }