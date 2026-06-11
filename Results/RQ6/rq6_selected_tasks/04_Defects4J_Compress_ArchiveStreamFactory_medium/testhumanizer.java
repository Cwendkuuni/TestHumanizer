@Test(timeout = 4000)
    public void testCreateArchiveInputStreamWithBufferedInputStream() throws Throwable {
        // Given: A BufferedInputStream that does not support mark/reset
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        PipedInputStream pipedInputStream = new PipedInputStream();
        BufferedInputStream bufferedInputStream = new BufferedInputStream(pipedInputStream);

        // When: Attempting to create an archive input stream
        // Then: Expect an exception due to unsupported mark/reset
        try {
            archiveStreamFactory.createArchiveInputStream((InputStream) bufferedInputStream);
            fail("Expecting exception: Exception");
        } catch (Exception e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateArchiveInputStreamWithNullInputStream() throws Throwable {
        // Given: A null InputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();

        // When: Attempting to create an archive input stream
        // Then: Expect an IllegalArgumentException
        try {
            archiveStreamFactory.createArchiveInputStream((InputStream) null);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateCpioArchiveOutputStream() throws Throwable {
        // Given: A valid MockPrintStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        MockPrintStream mockPrintStream = new MockPrintStream("cpio");

        // When: Creating a CPIO archive output stream
        ArchiveOutputStream archiveOutputStream = archiveStreamFactory.createArchiveOutputStream("cpio", mockPrintStream);

        // Then: The output stream should not be null
        assertNotNull("Expected a non-null ArchiveOutputStream", archiveOutputStream);
    }

    @Test(timeout = 4000)
    public void testCreateArchiveOutputStreamWithInvalidFormat() throws Throwable {
        // Given: An invalid archive format name
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        MockFile mockFile = new MockFile("InvalidFile", "InvalidFile");
        MockPrintStream mockPrintStream = new MockPrintStream(mockFile);

        // When: Attempting to create an archive output stream
        // Then: Expect an exception due to unknown format
        try {
            archiveStreamFactory.createArchiveOutputStream("xS", mockPrintStream);
            fail("Expecting exception: Exception");
        } catch (Exception e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateTarArchiveOutputStreamWithoutClassDef() throws Throwable {
        // Given: A ByteArrayOutputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();

        // When: Attempting to create a TAR archive output stream
        // Then: Expect a NoClassDefFoundError
        try {
            archiveStreamFactory.createArchiveOutputStream("tar", byteArrayOutputStream);
            fail("Expecting exception: NoClassDefFoundError");
        } catch (NoClassDefFoundError e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateZipArchiveOutputStream() throws Throwable {
        // Given: A PipedOutputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        PipedOutputStream pipedOutputStream = new PipedOutputStream();

        // When: Creating a ZIP archive output stream
        ZipArchiveOutputStream zipArchiveOutputStream = (ZipArchiveOutputStream) archiveStreamFactory.createArchiveOutputStream("zip", pipedOutputStream);

        // Then: Verify the compression method
        assertEquals("Expected DEFLATED compression method", 8, ZipArchiveOutputStream.DEFLATED);
    }

    @Test(timeout = 4000)
    public void testCreateJarArchiveOutputStream() throws Throwable {
        // Given: A ByteArrayOutputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();

        // When: Creating a JAR archive output stream
        JarArchiveOutputStream jarArchiveOutputStream = (JarArchiveOutputStream) archiveStreamFactory.createArchiveOutputStream("jar", byteArrayOutputStream);

        // Then: Verify the EFS_FLAG
        assertEquals("Expected EFS_FLAG value", 2048, ZipArchiveOutputStream.EFS_FLAG);
    }

    @Test(timeout = 4000)
    public void testCreateArchiveOutputStreamWithNullOutputStream() throws Throwable {
        // Given: A null OutputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();

        // When: Attempting to create an archive output stream
        // Then: Expect an IllegalArgumentException
        try {
            archiveStreamFactory.createArchiveOutputStream("5PMOWg}Da_dS&BS}*", (OutputStream) null);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateArchiveOutputStreamWithNullFormat() throws Throwable {
        // Given: A valid PipedOutputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        PipedOutputStream pipedOutputStream = new PipedOutputStream();

        // When: Attempting to create an archive output stream with null format
        // Then: Expect an IllegalArgumentException
        try {
            archiveStreamFactory.createArchiveOutputStream((String) null, pipedOutputStream);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateArArchiveOutputStream() throws Throwable {
        // Given: A PipedOutputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        PipedOutputStream pipedOutputStream = new PipedOutputStream();

        // When: Creating an AR archive output stream
        ArArchiveOutputStream arArchiveOutputStream = (ArArchiveOutputStream) archiveStreamFactory.createArchiveOutputStream("ar", pipedOutputStream);

        // Then: Verify the LONGFILE_ERROR constant
        assertEquals("Expected LONGFILE_ERROR value", 0, ArArchiveOutputStream.LONGFILE_ERROR);
    }

    @Test(timeout = 4000)
    public void testCreateArchiveInputStreamWithInvalidFormat() throws Throwable {
        // Given: A ByteArrayInputStream
        byte[] byteArray = new byte[15];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();

        // When: Attempting to create an archive input stream with an invalid format
        // Then: Expect an exception due to unknown format
        try {
            archiveStreamFactory.createArchiveInputStream("ustar\u0000", (InputStream) byteArrayInputStream);
            fail("Expecting exception: Exception");
        } catch (Exception e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateArchiveInputStreamWithUnsupportedMark() throws Throwable {
        // Given: A ByteArrayInputStream
        byte[] byteArray = new byte[4];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        ArchiveInputStream archiveInputStream = archiveStreamFactory.createArchiveInputStream("cpio", (InputStream) byteArrayInputStream);

        // When: Attempting to create an archive input stream with unsupported mark
        // Then: Expect an IllegalArgumentException
        try {
            archiveStreamFactory.createArchiveInputStream((InputStream) archiveInputStream);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateAutoDetectedArchiveInputStream() throws Throwable {
        // Given: A ByteArrayInputStream
        byte[] byteArray = new byte[8];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();

        // When: Creating an auto-detected archive input stream
        ArchiveInputStream archiveInputStream = archiveStreamFactory.createArchiveInputStream((InputStream) byteArrayInputStream);

        // Then: Verify the bytes read
        assertEquals("Expected bytes read to be 0", 0L, archiveInputStream.getBytesRead());
    }

    @Test(timeout = 4000)
    public void testCreateTarArchiveInputStream() throws Throwable {
        // Given: A ByteArrayInputStream wrapped in a BufferedInputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        byte[] byteArray = new byte[4];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveInputStream archiveInputStream = archiveStreamFactory.createArchiveInputStream((InputStream) byteArrayInputStream);
        BufferedInputStream bufferedInputStream = new BufferedInputStream(archiveInputStream);

        // When: Creating a TAR archive input stream
        ArchiveInputStream tarArchiveInputStream = archiveStreamFactory.createArchiveInputStream("tar", (InputStream) bufferedInputStream);

        // Then: Verify the streams are not the same
        assertNotSame("Expected different ArchiveInputStream instances", tarArchiveInputStream, archiveInputStream);
    }

    @Test(timeout = 4000)
    public void testCreateZipArchiveInputStream() throws Throwable {
        // Given: A ByteArrayInputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        byte[] byteArray = new byte[5];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveInputStream archiveInputStream = archiveStreamFactory.createArchiveInputStream((InputStream) byteArrayInputStream);

        // When: Creating a ZIP archive input stream
        ArchiveInputStream zipArchiveInputStream = archiveStreamFactory.createArchiveInputStream("zip", (InputStream) archiveInputStream);

        // Then: Verify the bytes read
        assertEquals("Expected bytes read to be 0", 0L, zipArchiveInputStream.getBytesRead());
    }

    @Test(timeout = 4000)
    public void testCreateArArchiveInputStream() throws Throwable {
        // Given: A ByteArrayInputStream
        byte[] byteArray = new byte[8];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();

        // When: Creating an AR archive input stream
        ArchiveInputStream arArchiveInputStream = archiveStreamFactory.createArchiveInputStream("ar", (InputStream) byteArrayInputStream);

        // Then: Verify the count
        assertEquals("Expected count to be 0", 0, arArchiveInputStream.getCount());
    }

    @Test(timeout = 4000)
    public void testCreateArchiveInputStreamWithNullFormat() throws Throwable {
        // Given: A ByteArrayInputStream
        byte[] byteArray = new byte[8];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        ArchiveInputStream archiveInputStream = archiveStreamFactory.createArchiveInputStream((InputStream) byteArrayInputStream);

        // When: Attempting to create an archive input stream with null format
        // Then: Expect an IllegalArgumentException
        try {
            archiveStreamFactory.createArchiveInputStream((String) null, (InputStream) archiveInputStream);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateDumpArchiveInputStreamWithUnexpectedEOF() throws Throwable {
        // Given: A ByteArrayInputStream
        byte[] byteArray = new byte[8];
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray);
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();
        ArchiveInputStream archiveInputStream = archiveStreamFactory.createArchiveInputStream((InputStream) byteArrayInputStream);

        // When: Attempting to create a DUMP archive input stream
        // Then: Expect an exception due to unexpected EOF
        try {
            archiveStreamFactory.createArchiveInputStream("dump", (InputStream) archiveInputStream);
            fail("Expecting exception: Exception");
        } catch (Exception e) {
            verifyException("org.apache.commons.compress.archivers.dump.DumpArchiveInputStream", e);
        }
    }

    @Test(timeout = 4000)
    public void testCreateTarArchiveInputStreamWithNullInputStream() throws Throwable {
        // Given: A null InputStream
        ArchiveStreamFactory archiveStreamFactory = new ArchiveStreamFactory();

        // When: Attempting to create a TAR archive input stream
        // Then: Expect an IllegalArgumentException
        try {
            archiveStreamFactory.createArchiveInputStream("tar", (InputStream) null);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.compress.archivers.ArchiveStreamFactory", e);
        }
    }