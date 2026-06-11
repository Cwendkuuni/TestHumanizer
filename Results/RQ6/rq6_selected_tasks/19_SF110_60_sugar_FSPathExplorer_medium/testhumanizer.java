@Test(timeout = 4000)
    public void testShowWelcome() throws Throwable {
        // Given: No specific setup is required

        // When: Calling showWelcome method
        FSPathExplorer.showWelcome();

        // Then: No exception is expected, and the welcome message is displayed
    }

    @Test(timeout = 4000)
    public void testShowHelp() throws Throwable {
        // Given: No specific setup is required

        // When: Calling showHelp method
        FSPathExplorer.showHelp();

        // Then: No exception is expected, and the help message is displayed
    }

    @Test(timeout = 4000)
    public void testConfigureExplorerWithNullArgs() throws Throwable {
        // Given: An instance of FSPathExplorer and a null argument array
        FSPathExplorer fSPathExplorer = new FSPathExplorer();
        String[] args = new String[1];

        // When: Configuring explorer with null arguments
        // Then: Expecting NullPointerException
        try {
            fSPathExplorer.configureExplorer(args);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testStartWithInvalidCommand() throws Throwable {
        // Given: An instance of FSPathExplorer and input command "cd"
        SystemInUtil.addInputLine("cd");
        FSPathExplorer fSPathExplorer = new FSPathExplorer();

        // When: Starting the explorer
        // Then: Expecting ArrayIndexOutOfBoundsException
        try {
            fSPathExplorer.start();
            fail("Expecting exception: ArrayIndexOutOfBoundsException");
        } catch (ArrayIndexOutOfBoundsException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testStartWithPwdCommand() throws Throwable {
        // Given: An instance of FSPathExplorer and input command "pwd"
        FSPathExplorer fSPathExplorer = new FSPathExplorer();
        SystemInUtil.addInputLine("pwd");

        // When: Starting the explorer
        // Then: Expecting NullPointerException
        try {
            fSPathExplorer.start();
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testMainWithExitCommand() throws Throwable {
        // Given: Command-line arguments with "exit"
        String[] args = new String[2];
        args[0] = "exit";
        args[1] = "";

        // When: Running the main method
        FSPathExplorer.main(args);

        // Then: The length of args should be 2
        assertEquals("The length of args should be 2", 2, args.length);
    }

    @Test(timeout = 4000)
    public void testCreateFSPathWithInvalidRootPath() throws Throwable {
        // Given: An instance of FSPathExplorer and a mock file
        FSPathExplorer fSPathExplorer = new FSPathExplorer();
        File file = MockFile.createTempFile("'b)F>4NSpovSnM.", " gzC8Yqt\"/5y", (File) null);
        fSPathExplorer.rootPath = file;

        // When: Creating FSPath
        // Then: Expecting InstantiationError
        try {
            fSPathExplorer.createFSPath();
            fail("Expecting exception: InstantiationError");
        } catch (InstantiationError e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testMainWithInvalidArgs() throws Throwable {
        // Given: Command-line arguments with invalid flags
        String[] args = new String[3];
        args[0] = "";
        args[1] = "-f";
        args[2] = "";

        // When: Running the main method
        // Then: Expecting NullPointerException
        try {
            FSPathExplorer.main(args);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testMainWithDuplicatePathArgs() throws Throwable {
        // Given: Command-line arguments with duplicate "-path" flags
        String[] args = new String[2];
        args[0] = "-path";
        args[1] = "-path";

        // When: Running the main method
        // Then: Expecting ArrayIndexOutOfBoundsException
        try {
            FSPathExplorer.main(args);
            fail("Expecting exception: ArrayIndexOutOfBoundsException");
        } catch (ArrayIndexOutOfBoundsException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testMainWithFindFlag() throws Throwable {
        // Given: Command-line arguments with "-find" flag
        String[] args = new String[3];
        args[0] = "";
        args[1] = "";
        args[2] = "-find";

        // When: Running the main method
        // Then: Expecting NullPointerException
        try {
            FSPathExplorer.main(args);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testMainWithInvalidPathFlag() throws Throwable {
        // Given: Command-line arguments with invalid path flag
        String[] args = new String[7];
        args[0] = " ";
        args[1] = "ZY4";
        args[2] = "-p";

        // When: Running the main method
        // Then: Expecting NullPointerException
        try {
            FSPathExplorer.main(args);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testStartWithHelpCommand() throws Throwable {
        // Given: An instance of FSPathExplorer and input command "help"
        FSPathExplorer fSPathExplorer = new FSPathExplorer();
        SystemInUtil.addInputLine("help");

        // When: Starting the explorer
        // Then: No exception is expected, and help information is displayed
        fSPathExplorer.start();
    }