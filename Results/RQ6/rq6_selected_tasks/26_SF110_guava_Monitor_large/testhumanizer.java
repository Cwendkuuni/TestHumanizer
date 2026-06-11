private static final long NEGATIVE_TIMEOUT = -319L;
    private static final long POSITIVE_TIMEOUT = 665L;
    private static final long ZERO_TIMEOUT = 0L;
    private static final long TIMEOUT_NANOSECONDS = 2456L;
    private static final long TIMEOUT_MILLISECONDS = 337L;
    private static final long TIMEOUT_DAYS = 0L;

    @Test(timeout = 4000)
    public void testWaitForUninterruptiblyWithNullGuardAndNegativeTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor(false);
        TimeUnit timeUnit = TimeUnit.HOURS;

        // When & Then
        try {
            monitor.waitForUninterruptibly(null, NEGATIVE_TIMEOUT, timeUnit);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testWaitForUninterruptiblyWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When & Then
        try {
            monitor.waitForUninterruptibly(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testWaitForWithNullGuardAndPositiveTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor(false);
        TimeUnit timeUnit = TimeUnit.MINUTES;

        // When & Then
        try {
            monitor.waitFor(null, POSITIVE_TIMEOUT, timeUnit);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testWaitForWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When & Then
        try {
            monitor.waitFor(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testTryEnterIfWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When & Then
        try {
            monitor.tryEnterIf(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testHasWaitersWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);

        // When & Then
        try {
            monitor.hasWaiters(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterWhenUninterruptiblyWithNullGuardAndMillisecondsTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor(false);
        TimeUnit timeUnit = TimeUnit.MILLISECONDS;

        // When & Then
        try {
            monitor.enterWhenUninterruptibly(null, TIMEOUT_MILLISECONDS, timeUnit);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterWhenUninterruptiblyWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When & Then
        try {
            monitor.enterWhenUninterruptibly(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterWhenWithNullGuardAndZeroTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);
        TimeUnit timeUnit = TimeUnit.MILLISECONDS;

        // When & Then
        try {
            monitor.enterWhen(null, ZERO_TIMEOUT, timeUnit);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterWhenWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When & Then
        try {
            monitor.enterWhen(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterIfInterruptiblyWithNullGuardAndDaysTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor(false);
        TimeUnit timeUnit = TimeUnit.DAYS;

        // When & Then
        try {
            monitor.enterIfInterruptibly(null, ZERO_TIMEOUT, timeUnit);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterIfInterruptiblyWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);

        // When & Then
        try {
            monitor.enterIfInterruptibly(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterIfWithNullGuardAndNanosecondsTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor();
        TimeUnit timeUnit = TimeUnit.NANOSECONDS;

        // When & Then
        try {
            monitor.enterIf(null, TIMEOUT_NANOSECONDS, timeUnit);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEnterAndLeave() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When
        monitor.enter();
        monitor.leave();

        // Then
        assertFalse("Monitor should not be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testEnterAndEnterInterruptiblyAndLeave() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When
        monitor.enter();
        monitor.enterInterruptibly();
        monitor.leave();

        // Then
        assertFalse("Monitor should not be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testEnterWithTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor();
        TimeUnit timeUnit = TimeUnit.NANOSECONDS;

        // When
        boolean entered = monitor.enter(TIMEOUT_NANOSECONDS, timeUnit);

        // Then
        assertFalse("Monitor should not be fair", monitor.isFair());
        assertTrue("Monitor should be entered", entered);
    }

    @Test(timeout = 4000)
    public void testEnterWithZeroTimeoutOnFairMonitor() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);
        TimeUnit timeUnit = TimeUnit.DAYS;

        // When
        monitor.enter(ZERO_TIMEOUT, timeUnit);

        // Then
        assertTrue("Monitor should be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testEnterInterruptiblyWithTimeout() throws Throwable {
        // Given
        Monitor monitor = new Monitor();
        TimeUnit timeUnit = TimeUnit.NANOSECONDS;

        // When
        monitor.enterInterruptibly(TIMEOUT_NANOSECONDS, timeUnit);

        // Then
        assertFalse("Monitor should not be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testTryEnter() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When
        monitor.tryEnter();

        // Then
        assertFalse("Monitor should not be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testIsFair() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);

        // When
        boolean isFair = monitor.isFair();

        // Then
        assertTrue("Monitor should be fair", isFair);
    }

    @Test(timeout = 4000)
    public void testIsOccupiedByCurrentThread() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);

        // When
        monitor.isOccupiedByCurrentThread();

        // Then
        assertTrue("Monitor should be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testHasQueuedThreads() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);

        // When
        monitor.hasQueuedThreads();

        // Then
        assertTrue("Monitor should be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testIsOccupied() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);

        // When
        monitor.isOccupied();

        // Then
        assertTrue("Monitor should be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testGetOccupiedDepth() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);

        // When
        monitor.getOccupiedDepth();

        // Then
        assertTrue("Monitor should be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testGetQueueLength() throws Throwable {
        // Given
        Monitor monitor = new Monitor();

        // When
        monitor.getQueueLength();

        // Then
        assertFalse("Monitor should not be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testHasQueuedThread() throws Throwable {
        // Given
        Monitor monitor = new Monitor(true);
        ThreadGroup threadGroup = mock(ThreadGroup.class, new ViolatedAssumptionAnswer());
        Thread thread = MockThread.currentThread();
        MockThread mockThread = new MockThread(threadGroup, thread, "");

        // When
        monitor.hasQueuedThread(mockThread);

        // Then
        assertTrue("Monitor should be fair", monitor.isFair());
    }

    @Test(timeout = 4000)
    public void testEnterIfWithNullGuard() throws Throwable {
        // Given
        Monitor monitor = new Monitor(false);

        // When & Then
        try {
            monitor.enterIf(null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }