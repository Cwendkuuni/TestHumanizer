package net.virtualinfinity.atrobots.gui.renderers;

import java.util.*;
import java.awt.*;
import java.awt.geom.*;
import net.virtualinfinity.atrobots.measures.*;
import net.virtualinfinity.atrobots.snapshots.*;

public class RobotRenderer implements SnapshotRenderer<RobotSnapshot>
{
    private boolean showStatusBars;
    private boolean renderDead;
    private boolean showName;
    private boolean fillShield;
    private static final Color HEAT_COLOR1;
    private static final Color HEAT_COLOR2;
    
    public RobotRenderer() {
        this.showStatusBars = true;
        this.renderDead = true;
        this.showName = true;
        this.fillShield = true;
    }
    
    @Override
    public void render(final Graphics2D g2d, final RobotSnapshot robotSnapshot, final Set<Integer> selectedRobotIds) {
        if (!this.isRenderDead() && robotSnapshot.isDead()) {
            return;
        }
        this.paintBody(g2d, robotSnapshot);
        if (!robotSnapshot.isDead()) {
            this.paintShield(g2d, robotSnapshot);
            this.paintTurret(g2d, robotSnapshot);
            if (this.isShowStatusBars()) {
                this.paintArmor(g2d, robotSnapshot);
                this.paintHeat(g2d, robotSnapshot);
            }
            if (this.isShowName()) {
                this.paintName(g2d, robotSnapshot);
            }
        }
        if (selectedRobotIds.contains(robotSnapshot.getId())) {
            this.paintSelection(g2d, robotSnapshot);
        }
    }
    
    public boolean isRenderDead() {
        return this.renderDead;
    }
    
    public void setRenderDead(final boolean renderDead) {
        this.renderDead = renderDead;
    }
    
    public boolean isShowStatusBars() {
        return this.showStatusBars;
    }
    
    public void setShowStatusBars(final boolean showStatusBars) {
        this.showStatusBars = showStatusBars;
    }
    
    public boolean isShowName() {
        return this.showName;
    }
    
    public void setShowName(final boolean showName) {
        this.showName = showName;
    }
    
    public boolean isFillShield() {
        return this.fillShield;
    }
    
    public void setFillShield(final boolean fillShield) {
        this.fillShield = fillShield;
    }
    
    private void paintSelection(final Graphics2D g2d, final RobotSnapshot robotSnapshot) {
        g2d.setPaint(new Color(1.0f, 1.0f, 0.0f, 0.25f));
        final Ellipse2D.Double s = new Ellipse2D.Double();
        s.setFrameFromCenter(robotSnapshot.getX(), robotSnapshot.getY(), robotSnapshot.getX() + 30.0, robotSnapshot.getY() + 30.0);
        g2d.fill(s);
    }
    
    private void paintShield(final Graphics2D g2d, final RobotSnapshot robotSnapshot) {
        if (robotSnapshot.isActiveShield()) {
            final Ellipse2D.Double s = new Ellipse2D.Double();
            s.setFrameFromCenter(robotSnapshot.getX(), robotSnapshot.getY(), robotSnapshot.getX() + 15.0, robotSnapshot.getY() + 15.0);
            if (this.isFillShield()) {
                g2d.setPaint(new RadialGradientPaint(robotSnapshot.getPositionVector().toPoint2D(), 15.0f, new float[] { 0.0f, 0.75f, 1.0f }, new Color[] { new Color(0.5f, 0.5f, 0.0f, 0.8f), new Color(0.0f, 0.0f, 0.5f, 0.1f), Color.white }));
                g2d.fill(s);
                g2d.fill(s);
            }
            else {
                g2d.setPaint(new Color(0.8f, 0.6f, 1.0f));
                g2d.draw(s);
            }
        }
    }
    
    private void paintName(final Graphics2D g2d, final RobotSnapshot robotSnapshot) {
        g2d.setPaint(Color.yellow);
        g2d.drawString(robotSnapshot.getName(), (float)(robotSnapshot.getX() - g2d.getFontMetrics().getStringBounds(robotSnapshot.getName(), g2d).getWidth() / 2.0), (float)(robotSnapshot.getY() - 10.0));
    }
    
    private void paintHeat(final Graphics2D g2d, final RobotSnapshot robotSnapshot) {
        final Rectangle2D.Double rect = new Rectangle2D.Double(robotSnapshot.getX() - 50.0, robotSnapshot.getY() + 35.0, 100.0, 10.0);
        g2d.setPaint(new GradientPaint((float)rect.getMinX(), (float)rect.getMinY(), RobotRenderer.HEAT_COLOR1, (float)rect.getMaxX(), (float)rect.getMinY(), RobotRenderer.HEAT_COLOR2));
        if (!robotSnapshot.isDead()) {
            g2d.fill(new Rectangle2D.Double(robotSnapshot.getX() - 50.0, robotSnapshot.getY() + 35.0, robotSnapshot.getTemperature().getLogScale() * 0.2, 10.0));
        }
        g2d.draw(rect);
    }
    
    private void paintArmor(final Graphics2D g2d, final RobotSnapshot robotSnapshot) {
        g2d.setPaint(new Color(0.0f, 0.0f, 1.0f, 0.6f));
        g2d.fill(new Rectangle2D.Double(robotSnapshot.getX() - 50.0, robotSnapshot.getY() + 20.0, robotSnapshot.getArmor(), 10.0));
        g2d.setPaint(new Color(0.0f, 1.0f, 0.0f, 0.6f));
        g2d.draw(new Rectangle2D.Double(robotSnapshot.getX() - 50.0, robotSnapshot.getY() + 20.0, 100.0, 10.0));
    }
    
    private void paintTurret(final Graphics2D g2d, final RobotSnapshot robotSnapshot) {
        g2d.setPaint(Color.white);
        g2d.draw(new Line2D.Double(robotSnapshot.getX(), robotSnapshot.getY(), robotSnapshot.getX() + robotSnapshot.getTurretHeading().cosine() * 5.0, robotSnapshot.getY() + robotSnapshot.getTurretHeading().sine() * 5.0));
    }
    
    private void paintBody(final Graphics2D g2d, final RobotSnapshot robotSnapshot) {
        final Stroke stroke = g2d.getStroke();
        if (robotSnapshot.isDead()) {
            final BasicStroke basicStroke = new BasicStroke(1.0f, 1, 0, 10.0f, new float[] { 5.0f, 5.0f }, 0.0f);
            g2d.setStroke(basicStroke);
            g2d.setPaint(Color.orange.darker().darker());
        }
        else {
            g2d.setPaint(Color.red);
        }
        final GeneralPath path = new GeneralPath();
        path.moveTo(robotSnapshot.getX() + robotSnapshot.getHeading().cosine() * 15.0, robotSnapshot.getY() + robotSnapshot.getHeading().sine() * 15.0);
        final AbsoluteAngle cc = robotSnapshot.getHeading().counterClockwise(RelativeAngle.fromBygrees(160));
        final AbsoluteAngle c = robotSnapshot.getHeading().clockwise(RelativeAngle.fromBygrees(160));
        path.lineTo(robotSnapshot.getX() + cc.cosine() * 9.0, robotSnapshot.getY() + cc.sine() * 9.0);
        path.lineTo(robotSnapshot.getX(), robotSnapshot.getY());
        path.lineTo(robotSnapshot.getX() + c.cosine() * 9.0, robotSnapshot.getY() + c.sine() * 9.0);
        path.closePath();
        if (robotSnapshot.isDead()) {
            g2d.draw(path);
        }
        else {
            g2d.fill(path);
        }
        g2d.setStroke(stroke);
    }
    
    static {
        HEAT_COLOR1 = new Color(1.0f, 0.0f, 0.0f, 0.1f);
        HEAT_COLOR2 = Color.yellow;
    }
}
