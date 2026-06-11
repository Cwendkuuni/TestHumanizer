package ghm.follow.gui;

import javax.swing.*;
import ghm.follow.config.*;
import java.awt.*;
import java.io.*;

public class TabbedPane extends JTabbedPane
{
    private FollowAppAttributes attributes;
    
    public TabbedPane(final FollowAppAttributes attributes) {
        super(attributes.getTabPlacement());
        this.attributes = null;
        this.attributes = attributes;
    }
    
    @Override
    public Component findComponentAt(final int x, final int y) {
        if (!this.contains(x, y)) {
            return null;
        }
        for (int ncomponents = this.getComponentCount(), i = 0; i < ncomponents; ++i) {
            Component comp = this.getComponentAt(i);
            if (comp != null) {
                if (comp instanceof Container) {
                    if (comp.isVisible()) {
                        comp = ((Container)comp).findComponentAt(x - comp.getX(), y - comp.getY());
                    }
                }
                else {
                    comp = comp.getComponentAt(x - comp.getX(), y - comp.getY());
                }
                if (comp != null && comp.isVisible()) {
                    return comp;
                }
            }
        }
        return this;
    }
    
    @Override
    public void setSelectedIndex(final int index) {
        super.setSelectedIndex(index);
        this.handleSelectedFile();
    }
    
    public void setSelectedComponent(final FileFollowingPane pane) {
        super.setSelectedComponent(pane);
        this.handleSelectedFile();
    }
    
    @Override
    public void removeTabAt(final int index) {
        super.removeTabAt(index);
        this.handleSelectedFile();
    }
    
    private void handleSelectedFile() {
        final FileFollowingPane pane = (FileFollowingPane)this.getSelectedComponent();
        if (pane != null) {
            final File parent = pane.getFollowedFile().getParentFile();
            this.attributes.setLastFileChooserDirectory(parent);
        }
    }
}
