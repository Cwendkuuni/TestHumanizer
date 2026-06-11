private static final int INTEGER_31 = 31;
    private static final int INTEGER_2 = 2;
    private static final long EXPIRATION_TIME_1 = 1L;
    private static final long EXPIRATION_TIME_810 = 810L;
    private static final long EXPIRATION_TIME_351 = 351L;
    private static final long EXPIRATION_TIME_2 = 2L;

    @Test(timeout = 4000)
    public void testExpiringMemoizingSupplierWithInteger() throws Throwable {
        // Given
        System.setCurrentTimeMillis(-1L);
        Integer integerInstance = INTEGER_31;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);
        TimeUnit timeUnit = TimeUnit.MICROSECONDS;

        // When
        Suppliers.ExpiringMemoizingSupplier<Integer> expiringMemoizingSupplier =
                new Suppliers.ExpiringMemoizingSupplier<>(supplier, EXPIRATION_TIME_1, timeUnit);
        Integer result = expiringMemoizingSupplier.get();

        // Then
        assertEquals("Expected the supplier to return the initial integer value", INTEGER_31, (int) result);
    }

    @Test(timeout = 4000)
    public void testExpiringMemoizingSupplierWithLocaleFilteringMode() throws Throwable {
        // Given
        Locale.FilteringMode filteringMode = Locale.FilteringMode.REJECT_EXTENDED_RANGES;
        Supplier<Locale.FilteringMode> supplier = Suppliers.ofInstance(filteringMode);
        TimeUnit timeUnit = TimeUnit.DAYS;

        // When
        Suppliers.ExpiringMemoizingSupplier<Locale.FilteringMode> expiringMemoizingSupplier =
                new Suppliers.ExpiringMemoizingSupplier<>(supplier, EXPIRATION_TIME_810, timeUnit);
        expiringMemoizingSupplier.expirationNanos = EXPIRATION_TIME_810;
        Locale.FilteringMode result = expiringMemoizingSupplier.get();

        // Then
        assertSame("Expected the supplier to return the initial filtering mode instance", filteringMode, result);
    }

    @Test(timeout = 4000)
    public void testMemoizingSupplierWithExpiringMemoizingSupplier() throws Throwable {
        // Given
        Integer integerInstance = INTEGER_2;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);
        Suppliers.MemoizingSupplier<Integer> memoizingSupplier = new Suppliers.MemoizingSupplier<>(supplier);
        TimeUnit timeUnit = TimeUnit.MILLISECONDS;

        // When
        Suppliers.ExpiringMemoizingSupplier<Integer> expiringMemoizingSupplier =
                new Suppliers.ExpiringMemoizingSupplier<>(memoizingSupplier, EXPIRATION_TIME_2, timeUnit);
        expiringMemoizingSupplier.get();
        Integer result = expiringMemoizingSupplier.get();

        // Then
        assertEquals("Expected the supplier to return the initial integer value", INTEGER_2, (int) result);
    }

    @Test(timeout = 4000)
    public void testMemoizeWithExpirationThrowsException() throws Throwable {
        // Given
        TimeUnit timeUnit = TimeUnit.NANOSECONDS;
        Locale.FilteringMode filteringMode = Locale.FilteringMode.AUTOSELECT_FILTERING;
        Supplier<Locale.FilteringMode> supplier = Suppliers.ofInstance(filteringMode);

        // When & Then
        try {
            Suppliers.memoizeWithExpiration(supplier, 0L, timeUnit);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testMemoizeSupplier() throws Throwable {
        // Given
        Integer integerInstance = INTEGER_31;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);

        // When
        Supplier<Integer> memoizedSupplier1 = Suppliers.memoize(supplier);
        Supplier<Integer> memoizedSupplier2 = Suppliers.memoize(memoizedSupplier1);

        // Then
        assertSame("Expected both memoized suppliers to be the same instance", memoizedSupplier1, memoizedSupplier2);
    }

    @Test(timeout = 4000)
    public void testSynchronizedMemoizingSupplierToString() throws Throwable {
        // Given
        Integer integerInstance = INTEGER_2;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);
        Supplier<Integer> synchronizedSupplier = Suppliers.synchronizedSupplier(supplier);
        Suppliers.MemoizingSupplier<Integer> memoizingSupplier = new Suppliers.MemoizingSupplier<>(synchronizedSupplier);
        TimeUnit timeUnit = TimeUnit.MILLISECONDS;

        // When
        Suppliers.ExpiringMemoizingSupplier<Integer> expiringMemoizingSupplier =
                new Suppliers.ExpiringMemoizingSupplier<>(memoizingSupplier, EXPIRATION_TIME_2, timeUnit);
        String result = expiringMemoizingSupplier.toString();

        // Then
        assertEquals("Expected the string representation to match the expected format",
                "Suppliers.memoizeWithExpiration(Suppliers.memoize(Suppliers.synchronizedSupplier(Suppliers.ofInstance(2)), 2000000, NANOS)", result);
    }

    @Test(timeout = 4000)
    public void testComposeSupplierWithIdentityConverter() throws Throwable {
        // Given
        Integer integerInstance = INTEGER_31;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);
        Converter<Integer, Integer> identityConverter = Converter.identity();

        // When
        Supplier<Integer> composedSupplier = Suppliers.compose((Function<? super Integer, Integer>) identityConverter, supplier);
        Suppliers.MemoizingSupplier<Integer> memoizingSupplier = new Suppliers.MemoizingSupplier<>(composedSupplier);
        Integer result = memoizingSupplier.get();

        // Then
        assertEquals("Expected the supplier to return the initial integer value", INTEGER_31, (int) result);
    }

    @Test(timeout = 4000)
    public void testComposeSupplierToString() throws Throwable {
        // Given
        Integer integerInstance = INTEGER_31;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);
        Converter<Integer, Integer> identityConverter = Converter.identity();

        // When
        Supplier<Integer> composedSupplier = Suppliers.compose((Function<? super Integer, Integer>) identityConverter, supplier);
        Suppliers.MemoizingSupplier<Integer> memoizingSupplier = new Suppliers.MemoizingSupplier<>(composedSupplier);
        String result = memoizingSupplier.toString();

        // Then
        assertEquals("Expected the string representation to match the expected format",
                "Suppliers.memoize(Suppliers.compose(Converter.identity(), Suppliers.ofInstance(31))", result);
    }

    @Test(timeout = 4000)
    public void testSynchronizedMemoizingSupplierGet() throws Throwable {
        // Given
        Integer integerInstance = INTEGER_2;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);
        Supplier<Integer> synchronizedSupplier = Suppliers.synchronizedSupplier(supplier);
        Suppliers.MemoizingSupplier<Integer> memoizingSupplier = new Suppliers.MemoizingSupplier<>(synchronizedSupplier);

        // When
        Integer result = memoizingSupplier.get();

        // Then
        assertEquals("Expected the supplier to return the initial integer value", INTEGER_2, (int) result);
    }

    @Test(timeout = 4000)
    public void testSupplierFunctionNotNull() throws Throwable {
        // When
        Function<Supplier<Integer>, Integer> function = Suppliers.supplierFunction();

        // Then
        assertNotNull("Expected the supplier function to be non-null", function);
    }

    @Test(timeout = 4000)
    public void testExpiringMemoizingSupplierWithMemoizingSupplier() throws Throwable {
        // Given
        Integer integerInstance = INTEGER_2;
        Supplier<Integer> supplier = Suppliers.ofInstance(integerInstance);
        Suppliers.MemoizingSupplier<Integer> memoizingSupplier = new Suppliers.MemoizingSupplier<>(supplier);
        memoizingSupplier.get();
        TimeUnit timeUnit = TimeUnit.MILLISECONDS;

        // When
        Suppliers.ExpiringMemoizingSupplier<Integer> expiringMemoizingSupplier =
                new Suppliers.ExpiringMemoizingSupplier<>(memoizingSupplier, EXPIRATION_TIME_2, timeUnit);
        Integer result = expiringMemoizingSupplier.get();

        // Then
        assertEquals("Expected the supplier to return the initial integer value", INTEGER_2, (int) result);
    }

    @Test(timeout = 4000)
    public void testExpiringMemoizingSupplierThrowsNullPointerException() throws Throwable {
        // Given
        Suppliers.MemoizingSupplier<Suppliers.ExpiringMemoizingSupplier<Integer>> memoizingSupplier =
                new Suppliers.MemoizingSupplier<>(null);
        Supplier<Suppliers.ExpiringMemoizingSupplier<Integer>> synchronizedSupplier =
                Suppliers.synchronizedSupplier(memoizingSupplier);
        TimeUnit timeUnit = TimeUnit.MILLISECONDS;

        // When & Then
        try {
            Suppliers.ExpiringMemoizingSupplier<Suppliers.ExpiringMemoizingSupplier<Integer>> expiringMemoizingSupplier =
                    new Suppliers.ExpiringMemoizingSupplier<>(synchronizedSupplier, EXPIRATION_TIME_351, timeUnit);
            expiringMemoizingSupplier.get();
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }