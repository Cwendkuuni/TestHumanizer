@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      boolean boolean0 = robotRenderer0.isShowStatusBars();
      assertTrue(robotRenderer0.isRenderDead());
      assertTrue(boolean0);
      assertTrue(robotRenderer0.isFillShield());
      assertTrue(robotRenderer0.isShowName());
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      boolean boolean0 = robotRenderer0.isShowName();
      assertTrue(boolean0);
      assertTrue(robotRenderer0.isFillShield());
      assertTrue(robotRenderer0.isRenderDead());
      assertTrue(robotRenderer0.isShowStatusBars());
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      boolean boolean0 = robotRenderer0.isRenderDead();
      assertTrue(boolean0);
      assertTrue(robotRenderer0.isFillShield());
      assertTrue(robotRenderer0.isShowName());
      assertTrue(robotRenderer0.isShowStatusBars());
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      boolean boolean0 = robotRenderer0.isFillShield();
      assertTrue(robotRenderer0.isRenderDead());
      assertTrue(robotRenderer0.isShowName());
      assertTrue(robotRenderer0.isShowStatusBars());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      RobotSnapshot robotSnapshot0 = new RobotSnapshot();
      AbsoluteAngle absoluteAngle0 = AbsoluteAngle.fromBygrees(354);
      Vector vector0 = absoluteAngle0.toUnitVector();
      robotSnapshot0.setPositionVector(vector0);
      robotSnapshot0.setTurretHeading(absoluteAngle0);
      LinkedHashSet<Integer> linkedHashSet0 = new LinkedHashSet<Integer>();
      robotSnapshot0.setHeading(absoluteAngle0);
      Stroke stroke0 = mock(Stroke.class, new ViolatedAssumptionAnswer());
      Temperature temperature0 = Temperature.BASE_TEMPERATURE;
      robotSnapshot0.setName("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer");
      robotSnapshot0.setTemperature(temperature0);
      Rectangle2D rectangle2D0 = mock(Rectangle2D.class, new ViolatedAssumptionAnswer());
      FontMetrics fontMetrics0 = mock(FontMetrics.class, new ViolatedAssumptionAnswer());
      Graphics2D graphics2D0 = mock(Graphics2D.class, new ViolatedAssumptionAnswer());
      doReturn((FontMetrics) null).when(graphics2D0).getFontMetrics();
      doReturn(stroke0).when(graphics2D0).getStroke();
      // Undeclared exception!
      try { 
        robotRenderer0.render(graphics2D0, robotSnapshot0, (Set<Integer>) linkedHashSet0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer", e);
      }
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      RobotSnapshot robotSnapshot0 = new RobotSnapshot();
      robotRenderer0.setFillShield(false);
      AbsoluteAngle absoluteAngle0 = AbsoluteAngle.fromBygrees((-1431));
      robotSnapshot0.setActiveShield(true);
      Vector vector0 = absoluteAngle0.toUnitVector();
      robotSnapshot0.setPositionVector(vector0);
      LinkedHashSet<Integer> linkedHashSet0 = new LinkedHashSet<Integer>();
      robotSnapshot0.setHeading(absoluteAngle0);
      Stroke stroke0 = mock(Stroke.class, new ViolatedAssumptionAnswer());
      Graphics2D graphics2D0 = mock(Graphics2D.class, new ViolatedAssumptionAnswer());
      doReturn(stroke0).when(graphics2D0).getStroke();
      // Undeclared exception!
      try { 
        robotRenderer0.render(graphics2D0, robotSnapshot0, (Set<Integer>) linkedHashSet0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer", e);
      }
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      RobotSnapshot robotSnapshot0 = new RobotSnapshot();
      AbsoluteAngle absoluteAngle0 = AbsoluteAngle.fromBygrees(354);
      robotRenderer0.setShowName(false);
      Vector vector0 = absoluteAngle0.toUnitVector();
      robotSnapshot0.setPositionVector(vector0);
      robotSnapshot0.setTurretHeading(absoluteAngle0);
      robotRenderer0.setShowStatusBars(false);
      assertFalse(robotRenderer0.isShowStatusBars());
      assertFalse(robotRenderer0.isShowName());
      
      LinkedHashSet<Integer> linkedHashSet0 = new LinkedHashSet<Integer>();
      robotSnapshot0.setHeading(absoluteAngle0);
      Stroke stroke0 = mock(Stroke.class, new ViolatedAssumptionAnswer());
      Graphics2D graphics2D0 = mock(Graphics2D.class, new ViolatedAssumptionAnswer());
      doReturn(stroke0).when(graphics2D0).getStroke();
      robotRenderer0.render(graphics2D0, robotSnapshot0, (Set<Integer>) linkedHashSet0);
      assertTrue(robotRenderer0.isFillShield());
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      assertTrue(robotRenderer0.isRenderDead());
      
      robotRenderer0.setRenderDead(false);
      assertFalse(robotRenderer0.isRenderDead());
      
      LinkedHashSet<Integer> linkedHashSet0 = new LinkedHashSet<Integer>();
      RobotSnapshot robotSnapshot0 = new RobotSnapshot();
      robotSnapshot0.setDead(true);
      robotRenderer0.render((Graphics2D) null, robotSnapshot0, (Set<Integer>) linkedHashSet0);
      assertTrue(robotRenderer0.isShowStatusBars());
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      robotRenderer0.setRenderDead(false);
      RobotSnapshot robotSnapshot0 = new RobotSnapshot();
      LinkedHashSet<Integer> linkedHashSet0 = new LinkedHashSet<Integer>();
      // Undeclared exception!
      try { 
        robotRenderer0.render((Graphics2D) null, robotSnapshot0, (Set<Integer>) linkedHashSet0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer", e);
      }
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      RobotSnapshot robotSnapshot0 = new RobotSnapshot();
      AbsoluteAngle absoluteAngle0 = AbsoluteAngle.fromBygrees(354);
      robotSnapshot0.setActiveShield(true);
      Vector vector0 = absoluteAngle0.toUnitVector();
      robotSnapshot0.setPositionVector(vector0);
      LinkedHashSet<Integer> linkedHashSet0 = new LinkedHashSet<Integer>();
      robotSnapshot0.setHeading(absoluteAngle0);
      Stroke stroke0 = mock(Stroke.class, new ViolatedAssumptionAnswer());
      Graphics2D graphics2D0 = mock(Graphics2D.class, new ViolatedAssumptionAnswer());
      doReturn(stroke0).when(graphics2D0).getStroke();
      // Undeclared exception!
      try { 
        robotRenderer0.render(graphics2D0, robotSnapshot0, (Set<Integer>) linkedHashSet0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer", e);
      }
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      RobotRenderer robotRenderer0 = new RobotRenderer();
      RobotSnapshot robotSnapshot0 = new RobotSnapshot();
      AbsoluteAngle absoluteAngle0 = AbsoluteAngle.fromBygrees((-3374));
      Vector vector0 = absoluteAngle0.toUnitVector();
      robotSnapshot0.setPositionVector(vector0);
      LinkedHashSet<Integer> linkedHashSet0 = new LinkedHashSet<Integer>();
      Integer integer0 = Integer.getInteger("net.virtualinfinity.atrobots.gui.renderers.RobotRenderer", 0);
      linkedHashSet0.add(integer0);
      Stroke stroke0 = mock(Stroke.class, new ViolatedAssumptionAnswer());
      Graphics2D graphics2D0 = mock(Graphics2D.class, new ViolatedAssumptionAnswer());
      doReturn(stroke0).when(graphics2D0).getStroke();
      robotSnapshot0.setDead(true);
      robotSnapshot0.setHeading(absoluteAngle0);
      robotRenderer0.render(graphics2D0, robotSnapshot0, (Set<Integer>) linkedHashSet0);
      assertTrue(robotRenderer0.isShowName());
      assertTrue(robotRenderer0.isRenderDead());
      assertTrue(robotRenderer0.isFillShield());
  }