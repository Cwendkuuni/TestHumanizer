package macaw.util;

import macaw.businessLayer.*;
import java.awt.*;
import macaw.system.*;
import javax.swing.*;
import java.util.*;
import java.awt.event.*;

public class DisplayableListPanel implements ActionListener
{
    private boolean isNewRecord;
    private ArrayList<Displayable> masterList;
    private SessionProperties sessionProperties;
    private Log log;
    private String panelTitleText;
    private String currentUserID;
    private UserInterfaceFactory userInterfaceFactory;
    private DisplayableListParentForm parentForm;
    private DisplayableListItemSelector listItemSelector;
    private DisplayableListItemAdder listItemAdder;
    private DisplayableListItemEditor listItemEditor;
    private DisplayableListItemViewer listItemViewer;
    private DisplayableListItemDeleter listItemDeleter;
    private String listOwnerName;
    private boolean allowWriteAccess;
    private boolean allowRecordEditing;
    private ArrayList<Displayable> masterSourceVariableCollection;
    private JPanel panel;
    private DisplayableList displayableList;
    private JButton select;
    private JButton add;
    private JButton edit;
    private JButton view;
    private JButton delete;
    
    public DisplayableListPanel(final SessionProperties sessionProperties, final DisplayableListParentForm parentForm, final String panelTitleText, final boolean allowWriteAccess) {
        this.init(sessionProperties, parentForm, panelTitleText, allowWriteAccess, allowWriteAccess);
    }
    
    public DisplayableListPanel(final SessionProperties sessionProperties, final DisplayableListParentForm parentForm, final String panelTitleText, final boolean allowWriteAccess, final boolean allowRecordEditing) {
        this.init(sessionProperties, parentForm, panelTitleText, allowWriteAccess, allowRecordEditing);
    }
    
    private void init(final SessionProperties sessionProperties, final DisplayableListParentForm parentForm, final String panelTitleText, final boolean allowWriteAccess, final boolean allowRecordEditing) {
        this.sessionProperties = sessionProperties;
        this.log = sessionProperties.getLog();
        this.parentForm = parentForm;
        this.panelTitleText = panelTitleText;
        this.allowWriteAccess = allowWriteAccess;
        this.allowRecordEditing = allowRecordEditing;
        this.userInterfaceFactory = sessionProperties.getUserInterfaceFactory();
        final User currentUser = (User)sessionProperties.getProperty("currentUser");
        this.currentUserID = currentUser.getUserID();
        this.masterList = new ArrayList<Displayable>();
        this.displayableList = new DisplayableList(this.userInterfaceFactory);
        final String selectText = MacawMessages.getMessage("general.buttons.select");
        (this.select = this.userInterfaceFactory.createButton(selectText)).addActionListener(this);
        final String addText = MacawMessages.getMessage("general.buttons.add");
        (this.add = this.userInterfaceFactory.createButton(addText)).addActionListener(this);
        final String editText = MacawMessages.getMessage("general.buttons.edit");
        (this.edit = this.userInterfaceFactory.createButton(editText)).addActionListener(this);
        final String viewText = MacawMessages.getMessage("general.buttons.view");
        (this.view = this.userInterfaceFactory.createButton(viewText)).addActionListener(this);
        final String deleteText = MacawMessages.getMessage("general.buttons.delete");
        (this.delete = this.userInterfaceFactory.createButton(deleteText)).addActionListener(this);
    }
    
    private void buildUI() {
        this.panel = this.userInterfaceFactory.createPanel();
        final GridBagConstraints panelGC = this.userInterfaceFactory.createGridBagConstraints();
        final JLabel titleLabel = this.userInterfaceFactory.createLabel(this.panelTitleText);
        this.panel.add(titleLabel, panelGC);
        final GridBagConstraints gridBagConstraints = panelGC;
        ++gridBagConstraints.gridy;
        panelGC.fill = 1;
        panelGC.weightx = 100.0;
        panelGC.weighty = 100.0;
        final JScrollPane scrollPane = this.displayableList.getListScrollPane();
        this.panel.add(scrollPane, panelGC);
        final GridBagConstraints gridBagConstraints2 = panelGC;
        ++gridBagConstraints2.gridy;
        panelGC.anchor = 14;
        panelGC.fill = 0;
        panelGC.weightx = 0.0;
        panelGC.weighty = 0.0;
        this.panel.add(this.createControlButtonPanel(), panelGC);
    }
    
    private JPanel createControlButtonPanel() {
        final JPanel panel = this.userInterfaceFactory.createPanel();
        final GridBagConstraints panelGC = this.userInterfaceFactory.createGridBagConstraints();
        if (this.listItemSelector != null && this.allowWriteAccess) {
            panel.add(this.select, panelGC);
            final GridBagConstraints gridBagConstraints = panelGC;
            ++gridBagConstraints.gridx;
        }
        if (this.listItemAdder != null) {
            panel.add(this.add, panelGC);
            final GridBagConstraints gridBagConstraints2 = panelGC;
            ++gridBagConstraints2.gridx;
        }
        if (this.allowRecordEditing && this.listItemEditor != null) {
            panel.add(this.edit, panelGC);
            final GridBagConstraints gridBagConstraints3 = panelGC;
            ++gridBagConstraints3.gridx;
        }
        else if (this.listItemViewer != null) {
            panel.add(this.view, panelGC);
            final GridBagConstraints gridBagConstraints4 = panelGC;
            ++gridBagConstraints4.gridx;
        }
        if (this.listItemDeleter != null) {
            panel.add(this.delete, panelGC);
        }
        return panel;
    }
    
    public void setNewRecord(final boolean isNewRecord) {
        this.isNewRecord = isNewRecord;
        this.updateButtonStates();
    }
    
    public JPanel getPanel() {
        this.buildUI();
        return this.panel;
    }
    
    public void setDisplayableListItemSelector(final DisplayableListItemSelector listItemSelector) {
        this.listItemSelector = listItemSelector;
    }
    
    public void setDisplayableListItemAdder(final DisplayableListItemAdder listItemAdder) {
        this.listItemAdder = listItemAdder;
    }
    
    public void setDisplayableListItemEditor(final DisplayableListItemEditor listItemEditor) {
        this.listItemEditor = listItemEditor;
    }
    
    public void setDisplayableListItemViewer(final DisplayableListItemViewer listItemViewer) {
        this.listItemViewer = listItemViewer;
    }
    
    public void setDisplayableListItemDeleter(final DisplayableListItemDeleter listItemDeleter) {
        this.listItemDeleter = listItemDeleter;
    }
    
    public void addListItem() {
        try {
            if (this.listItemAdder == null) {
                final String errorMessage = MacawMessages.getMessage("displayListPanel.error.missingAdder");
                final MacawException exception = new MacawException(MacawErrorType.MISSING_DISPLAY_LIST_ADDER, errorMessage);
                throw exception;
            }
            this.parentForm.commitChanges();
            this.listItemAdder.addItems(this.listOwnerName, this.displayableList);
            this.updateButtonStates();
        }
        catch (MacawException exception2) {
            final Log log = this.sessionProperties.getLog();
            log.displayErrorDialog(exception2);
        }
    }
    
    private void editSelectedListItem() {
        if (!this.displayableList.itemsAreSelected()) {
            final String errorMessage = MacawMessages.getMessage("general.error.unselectedItems");
            final Log log = (Log)this.sessionProperties.getProperty("log");
            log.displayErrorDialog(errorMessage);
            return;
        }
        try {
            if (this.listItemEditor == null) {
                final String errorMessage = MacawMessages.getMessage("displayListPanel.error.missingEditor");
                final MacawException exception = new MacawException(MacawErrorType.MISSING_DISPLAY_LIST_EDITOR, errorMessage);
                throw exception;
            }
            this.parentForm.commitChanges();
            final Displayable selectedListItem = this.displayableList.getSelectedItem();
            final String oldDisplayName = selectedListItem.getDisplayName();
            this.listItemEditor.editListItem(this.listOwnerName, selectedListItem, this.displayableList);
        }
        catch (MacawException exception2) {
            final Log log = this.sessionProperties.getLog();
            log.displayErrorDialog(exception2);
        }
    }
    
    private void viewSelectedListItem() {
        if (!this.displayableList.itemsAreSelected()) {
            final String errorMessage = MacawMessages.getMessage("general.error.unselectedItems");
            final Log log = (Log)this.sessionProperties.getProperty("log");
            log.displayErrorDialog(errorMessage);
            return;
        }
        try {
            if (this.listItemViewer == null) {
                final String errorMessage = MacawMessages.getMessage("displayListPanel.error.missingViewer");
                final MacawException exception = new MacawException(MacawErrorType.MISSING_DISPLAY_LIST_SELECTOR, errorMessage);
                throw exception;
            }
            final Displayable selectedListItem = this.displayableList.getSelectedItem();
            this.listItemViewer.viewListItem(selectedListItem);
        }
        catch (MacawException exception2) {
            final Log log = this.sessionProperties.getLog();
            log.displayErrorDialog(exception2);
        }
    }
    
    public void deleteSelectedListItems() {
        if (!this.displayableList.itemsAreSelected()) {
            final String errorMessage = MacawMessages.getMessage("general.error.unselectedItems");
            final Log log = this.sessionProperties.getLog();
            log.displayErrorDialog(errorMessage);
            return;
        }
        try {
            this.parentForm.commitChanges();
            if (this.listItemDeleter == null) {
                final String errorMessage = MacawMessages.getMessage("displayListPanel.error.missingDeleter");
                final MacawException exception = new MacawException(MacawErrorType.MISSING_DISPLAY_LIST_DELETER, errorMessage);
                throw exception;
            }
            final String dialogTitle = MacawMessages.getMessage("general.warning.title");
            final String warningMessage = MacawMessages.getMessage("general.warning.deletionIsPermanent");
            final int result = JOptionPane.showConfirmDialog(null, warningMessage, dialogTitle, 0, 2);
            if (result != 0) {
                return;
            }
            this.listItemDeleter.deleteListItems(this.listOwnerName, this.displayableList);
            this.updateButtonStates();
        }
        catch (MacawException exception2) {
            this.log.displayErrorDialog(exception2);
        }
    }
    
    private void selectListItems() {
        try {
            this.listItemSelector.selectListItems(this.listOwnerName, this.displayableList);
            this.updateButtonStates();
        }
        catch (MacawException exception) {
            this.log.displayErrorDialog(exception);
        }
    }
    
    public void updateButtonStates() {
        if (this.allowWriteAccess) {
            if (this.isNewRecord) {
                this.add.setEnabled(false);
                this.delete.setEnabled(false);
                this.edit.setEnabled(false);
                this.view.setEnabled(false);
                this.select.setEnabled(false);
            }
            else {
                this.add.setEnabled(true);
                this.select.setEnabled(true);
                if (this.displayableList.isEmpty()) {
                    this.delete.setEnabled(false);
                    if (this.allowRecordEditing) {
                        this.edit.setEnabled(false);
                    }
                    else {
                        this.view.setEnabled(false);
                    }
                }
                else {
                    this.delete.setEnabled(true);
                    if (this.allowRecordEditing) {
                        this.edit.setEnabled(true);
                    }
                    else {
                        this.view.setEnabled(true);
                    }
                }
            }
        }
        else {
            this.add.setEnabled(false);
            this.delete.setEnabled(false);
            if (this.displayableList.isEmpty()) {
                this.view.setEnabled(false);
            }
            else if (!this.isNewRecord) {
                this.view.setEnabled(true);
            }
        }
    }
    
    public void setDisplayableItems(final ArrayList<Displayable> masterList) {
        this.masterList = masterList;
        this.displayableList.setDisplayItems(masterList);
        this.updateButtonStates();
    }
    
    public void save() {
        this.masterList.clear();
        final ArrayList<Displayable> currentList = this.displayableList.getAllItems();
        this.masterList.addAll(currentList);
    }
    
    public ArrayList<Displayable> getAllListItems() {
        return this.displayableList.getAllItems();
    }
    
    public void setListOwnerName(final String listOwnerName) {
        this.listOwnerName = listOwnerName;
    }
    
    @Override
    public void actionPerformed(final ActionEvent event) {
        final Object button = event.getSource();
        if (button == this.select) {
            this.selectListItems();
        }
        else if (button == this.add) {
            this.addListItem();
        }
        else if (button == this.edit) {
            this.editSelectedListItem();
        }
        else if (button == this.view) {
            this.viewSelectedListItem();
        }
        else if (button == this.delete) {
            this.deleteSelectedListItems();
        }
    }
}
