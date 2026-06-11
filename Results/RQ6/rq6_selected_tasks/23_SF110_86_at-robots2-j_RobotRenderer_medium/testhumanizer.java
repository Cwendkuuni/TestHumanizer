// Constants for test setup
    private static final double CARTESIAN_COORDINATE = -4186.28;
    private static final double TEMPERATURE_LOG_SCALE = 0.2;
    private static final String ROBOT_NAME = "net.virtualinfinity.atrobots.snapshots.ScanSnapshot";

    @Test(timeout = 4000)
    public void testDefaultRendererSettings() throws Throwable {
        // Given: A new RobotRenderer instance
        RobotRenderer robotRenderer = new RobotRenderer();

        // Then: Verify default settings
        assertTrue("Expected fillShield to be true by default", robotRenderer.isFillShield());
        assertTrue("Expected renderDead to be true by default", robotRenderer.isRenderDead());
        assertTrue("Expected showStatusBars to be true by default", robotRenderer.isShowStatusBars());
        assertTrue("Expected showName to be true by default", robotRenderer.isShowName());
    }

    @Test(timeout = 4000)
    public void testRenderWithMockedGraphics() throws Throwable {
        // Given: A RobotSnapshot with specific settings
        RobotSnapshot robotSnapshot = createRobotSnapshotWithDefaults();
        LinkedHashSet<Integer> selectedRobotIds = new LinkedHashSet<>();
        RobotRenderer robotRenderer = new RobotRenderer();
        Graphics2D graphics2D = createMockedGraphics2D();

        // When: Rendering the robot
        robotRenderer.render(graphics2D, robotSnapshot, selectedRobotIds);

        // Then: Verify rendering behavior
        assertTrue("Expected showName to be true", robotRenderer.isShowName());
    }

    @Test(timeout = 4000)
    public void testRenderWithInactiveShield() throws Throwable {
        // Given: A RobotSnapshot with inactive shield
        RobotSnapshot robotSnapshot = createRobotSnapshotWithDefaults();
        robotSnapshot.setActiveShield(false);
        LinkedHashSet<Integer> selectedRobotIds = new LinkedHashSet<>();
        RobotRenderer robotRenderer = new RobotRenderer();
        robotRenderer.setFillShield(false);
        Graphics2D graphics2D = createMockedGraphics2D();

        // When: Rendering the robot
        try {
            robotRenderer.render(graphics2D, robotSnapshot, selectedRobotIds);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Then: Verify exception is thrown
            verifyException("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer", e);
        }
    }

    @Test(timeout = 4000)
    public void testRenderDeadRobot() throws Throwable {
        // Given: A dead RobotSnapshot
        RobotSnapshot robotSnapshot = new RobotSnapshot();
        robotSnapshot.setDead(true);
        LinkedHashSet<Integer> selectedRobotIds = new LinkedHashSet<>();
        RobotRenderer robotRenderer = new RobotRenderer();
        Graphics2D graphics2D = createMockedGraphics2D();

        // When: Rendering the robot
        robotRenderer.render(graphics2D, robotSnapshot, selectedRobotIds);

        // Then: Verify rendering behavior
        assertTrue("Expected renderDead to be true", robotRenderer.isRenderDead());
        assertTrue("Expected showStatusBars to be true", robotRenderer.isShowStatusBars());
        assertTrue("Expected fillShield to be true", robotRenderer.isFillShield());
        assertTrue("Expected showName to be true", robotRenderer.isShowName());
    }

    @Test(timeout = 4000)
    public void testRenderWithNullGraphics() throws Throwable {
        // Given: A RobotSnapshot and null Graphics2D
        RobotSnapshot robotSnapshot = new RobotSnapshot();
        LinkedHashSet<Integer> selectedRobotIds = new LinkedHashSet<>();
        RobotRenderer robotRenderer = new RobotRenderer();
        robotRenderer.setRenderDead(false);

        // When: Rendering the robot
        try {
            robotRenderer.render(null, robotSnapshot, selectedRobotIds);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Then: Verify exception is thrown
            verifyException("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer", e);
        }
    }

    private RobotSnapshot createRobotSnapshotWithDefaults() {
        RobotSnapshot robotSnapshot = new RobotSnapshot();
        AbsoluteAngle absoluteAngle = AbsoluteAngle.fromCartesian(CARTESIAN_COORDINATE, CARTESIAN_COORDINATE);
        robotSnapshot.setHeading(absoluteAngle);
        Vector vector = absoluteAngle.toUnitVector();
        Temperature temperature = Temperature.fromLogScale(TEMPERATURE_LOG_SCALE);
        robotSnapshot.setTemperature(temperature);
        robotSnapshot.setPositionVector(vector);
        robotSnapshot.setTurretHeading(absoluteAngle);
        robotSnapshot.setName(ROBOT_NAME);
        return robotSnapshot;
    }

    private Graphics2D createMockedGraphics2D() {
        Rectangle2D rectangle2D = mock(Rectangle2D.class, new ViolatedAssumptionAnswer());
        doReturn(0.0).when(rectangle2D).getWidth();
        FontMetrics fontMetrics = mock(FontMetrics.class, new ViolatedAssumptionAnswer());
        doReturn(rectangle2D).when(fontMetrics).getStringBounds(anyString(), any(java.awt.Graphics.class));
        Stroke stroke = mock(Stroke.class, new ViolatedAssumptionAnswer());
        Graphics2D graphics2D = mock(Graphics2D.class, new ViolatedAssumptionAnswer());
        doReturn(fontMetrics).when(graphics2D).getFontMetrics();
        doReturn(stroke).when(graphics2D).getStroke();
        return graphics2D;
    }