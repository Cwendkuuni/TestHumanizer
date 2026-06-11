@Test(timeout = 4000)
    public void testReadZeroBytesFromEmptyStream() throws Throwable {
        // Given: A mock enumeration with no elements
        Enumeration<FilterInputStream> emptyEnumeration = (Enumeration<FilterInputStream>) mock(Enumeration.class, new ViolatedAssumptionAnswer());
        doReturn(false).when(emptyEnumeration).hasMoreElements();
        SequenceInputStream sequenceInputStream = new SequenceInputStream(emptyEnumeration);
        DeflateCompressorInputStream deflateCompressorInputStream = new DeflateCompressorInputStream(sequenceInputStream);
        byte[] buffer = new byte[5];

        // When: Reading zero bytes from the stream
        int bytesRead = deflateCompressorInputStream.read(buffer, 0, 0);

        // Then: The number of bytes read should be zero
        assertEquals("Expected to read 0 bytes", 0, bytesRead);
    }

    @Test(timeout = 4000)
    public void testGetBytesReadInitiallyZero() throws Throwable {
        // Given: A piped input stream with a single byte buffer
        PipedInputStream pipedInputStream = new PipedInputStream(1);
        DeflateParameters deflateParameters = new DeflateParameters();
        deflateParameters.setWithZlibHeader(false);
        DeflateCompressorInputStream deflateCompressorInputStream = new DeflateCompressorInputStream(pipedInputStream, deflateParameters);

        // Then: Initially, no bytes should be read
        assertEquals("Expected initial bytes read to be 0", 0L, deflateCompressorInputStream.getBytesRead());
    }

    @Test(timeout = 4000)
    public void testAvailableReturnsOne() throws Throwable {
        // Given: A piped input stream
        PipedInputStream pipedInputStream = new PipedInputStream();
        DeflateCompressorInputStream deflateCompressorInputStream = new DeflateCompressorInputStream(pipedInputStream);

        // When: Checking available bytes
        int availableBytes = deflateCompressorInputStream.available();

        // Then: Available bytes should be 1
        assertEquals("Expected available bytes to be 1", 1, availableBytes);
    }

    @Test(timeout = 4000)
    public void testReadFromUnconnectedPipeThrowsIOException() throws Throwable {
        // Given: A piped input stream
        PipedInputStream pipedInputStream = new PipedInputStream();
        DeflateCompressorInputStream deflateCompressorInputStream = new DeflateCompressorInputStream(pipedInputStream);
        DeflateCompressorInputStream nestedDeflateCompressorInputStream = new DeflateCompressorInputStream(deflateCompressorInputStream);

        // When & Then: Reading from an unconnected pipe should throw IOException
        try {
            nestedDeflateCompressorInputStream.read();
            fail("Expecting exception: IOException");
        } catch (IOException e) {
            verifyException("java.io.PipedInputStream", e);
        }
    }

    @Test(timeout = 4000)
    public void testSkipOnUnconnectedPipeThrowsIOException() throws Throwable {
        // Given: A piped input stream with a single byte buffer
        PipedInputStream pipedInputStream = new PipedInputStream(1);
        DeflateCompressorInputStream deflateCompressorInputStream = new DeflateCompressorInputStream(pipedInputStream);

        // When & Then: Skipping bytes on an unconnected pipe should throw IOException
        try {
            deflateCompressorInputStream.skip(1);
            fail("Expecting exception: IOException");
        } catch (IOException e) {
            verifyException("java.io.PipedInputStream", e);
        }
    }

    @Test(timeout = 4000)
    public void testCloseStreamResetsBytesRead() throws Throwable {
        // Given: A piped input stream
        PipedInputStream pipedInputStream = new PipedInputStream();
        DeflateCompressorInputStream deflateCompressorInputStream = new DeflateCompressorInputStream(pipedInputStream);

        // When: Closing the stream
        deflateCompressorInputStream.close();

        // Then: Bytes read should be reset to 0
        assertEquals("Expected bytes read to be reset to 0 after closing", 0L, deflateCompressorInputStream.getBytesRead());
    }