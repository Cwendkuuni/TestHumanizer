import java.util.*;
import java.io.*;

public class Menu implements Runnable
{
    private String strTitle;
    private String strPicPath;
    private String strAudioPath;
    private String strTextFilePath;
    private String dvd_menu;
    private String[] titles;
    private boolean pal_menu;
    private String baseErr;
    private String[] video_files;
    private GUI m_GUI;
    private Thread m_Thread;
    private boolean m_Error;
    
    public Menu() {
        this.dvd_menu = "dvd-menu";
        this.titles = new String[50];
        this.baseErr = "Menu Error - ";
    }
    
    public Menu(final String title, final String TextFilePath, final boolean isPAL, final GUI DVD_GUI) {
        this.dvd_menu = "dvd-menu";
        this.titles = new String[50];
        this.baseErr = "Menu Error - ";
        this.strTitle = title;
        this.strTextFilePath = TextFilePath;
        this.pal_menu = isPAL;
        this.m_GUI = DVD_GUI;
    }
    
    public Menu(final String title, final String picPath, final String audioPath, final String TextFilePath, final boolean isPAL, final GUI DVD_GUI) {
        this.dvd_menu = "dvd-menu";
        this.titles = new String[50];
        this.baseErr = "Menu Error - ";
        this.strTitle = title;
        this.strPicPath = picPath;
        this.strAudioPath = audioPath;
        this.strTextFilePath = TextFilePath;
        this.pal_menu = isPAL;
        this.m_GUI = DVD_GUI;
    }
    
    public boolean init() {
        (this.m_Thread = new Thread(this)).start();
        try {
            this.m_Thread.join();
        }
        catch (InterruptedException ex) {
            ex.printStackTrace();
        }
        return this.m_Error || this.m_GUI.ErrorCheck(this.m_GUI.strOutputDir + "/log/dvd-menu.log");
    }
    
    @Override
    public void run() {
        this.DVDMainMenu();
    }
    
    public void DVDMainMenu() {
        final File ListDir = new File(this.m_GUI.strOutputDir);
        final FilenameFilter filter = new FilenameFilter() {
            boolean ret_val = true;
            
            @Override
            public boolean accept(final File dir, final String name) {
                if (name.endsWith("vob")) {
                    if (!name.equals("menu.vob")) {
                        this.ret_val = true;
                    }
                    else {
                        this.ret_val = false;
                    }
                }
                else {
                    this.ret_val = false;
                }
                return this.ret_val;
            }
        };
        this.video_files = ListDir.list(filter);
        this.m_GUI.lblAuthor.setEnabled(true);
        this.m_GUI.lblAuthorProg.setEnabled(true);
        this.m_GUI.prgAuthor.setEnabled(true);
        this.m_GUI.prgAuthor.setIndeterminate(true);
        String menu_options;
        if (this.strPicPath == null && this.strAudioPath == null) {
            menu_options = " -c -D -n '" + this.strTitle + "' -o " + this.m_GUI.strOutputDir;
        }
        else if (this.strPicPath.equals("") && this.strAudioPath != null) {
            menu_options = " -c -D -n '" + this.strTitle + "' -o " + this.m_GUI.strOutputDir + " -a " + this.strAudioPath;
        }
        else if (this.strPicPath != null && this.strAudioPath.equals("")) {
            menu_options = " -c -D -n '" + this.strTitle + "' -o " + this.m_GUI.strOutputDir + " -b " + this.strPicPath;
        }
        else {
            menu_options = " -c -D -n '" + this.strTitle + "' -o " + this.m_GUI.strOutputDir + " -a " + this.strAudioPath + " -b " + this.strPicPath;
        }
        int i = 0;
        if (this.strTextFilePath.equals("") || this.strTextFilePath == null) {
            while (i < this.video_files.length) {
                menu_options = menu_options + " -f " + this.m_GUI.strOutputDir + "/" + this.video_files[i].substring(0, 11) + ".vob -t " + this.strTitle + "_" + (i + 1);
                ++i;
            }
        }
        else {
            try {
                final BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(this.m_GUI.txtTextFile.getText())));
                i = 0;
                String line;
                while ((line = in.readLine()) != null) {
                    this.titles[i] = line;
                    ++i;
                }
                int num_blanks = 0;
                for (i = 0; i < this.titles.length; ++i) {
                    if (this.titles[i].equals("BLANK")) {
                        ++num_blanks;
                    }
                    if (this.titles[i].equals("DONE")) {
                        break;
                    }
                }
                final int num_lines = i;
                if (num_lines - num_blanks > 10) {
                    this.m_GUI.MessageBox("Your text file can only have a maximumof 10 titles!  Please edit your text file and rerundvd-homevideo.", 1);
                    this.m_Error = true;
                }
                else if (num_lines == this.video_files.length) {
                    for (i = 0; i < this.video_files.length; ++i) {
                        if (!this.titles[i].equals("BLANK") && !this.titles[i].equals("DONE")) {
                            menu_options = menu_options + " -t " + this.titles[i] + " -f " + this.m_GUI.strOutputDir + "/" + this.video_files[i].substring(0, 11) + ".vob";
                        }
                        else {
                            if (this.titles[i].equals("DONE")) {
                                break;
                            }
                            menu_options = menu_options + " -f " + this.m_GUI.strOutputDir + "/" + this.video_files[i].substring(0, 11) + ".vob";
                        }
                    }
                }
                else {
                    this.m_GUI.MessageBox("It appears that your text file is not\nformatted correctly.  You currently have\n" + (this.video_files.length + 1) + " vob files, \n" + "however your text file is showing\n" + num_lines + " lines.", 1);
                    this.m_Error = true;
                }
            }
            catch (FileNotFoundException ex) {
                SaveStackTrace.printTrace(this.m_GUI.strOutputDir, ex);
                this.m_GUI.MessageBox("Can not find " + this.m_GUI.txtTextFile + "\n" + ex.toString(), 0);
                ex.printStackTrace();
                this.m_Error = true;
            }
            catch (IOException ex2) {
                SaveStackTrace.printTrace(this.m_GUI.strOutputDir, ex2);
                this.m_GUI.MessageBox(this.baseErr + "IO Error\n" + ex2.toString(), 0);
                ex2.printStackTrace();
                this.m_Error = true;
            }
        }
        if (this.pal_menu) {
            menu_options += " -p";
        }
        this.dvd_menu = this.dvd_menu + menu_options + " 2>&1";
        this.m_GUI.txtAreaOutput.append(this.dvd_menu + "\n");
        try {
            final String[] dvd_menu_cmd = { "/bin/sh", "-c", this.dvd_menu };
            Process p = Runtime.getRuntime().exec(dvd_menu_cmd, null, new File(this.m_GUI.strOutputDir));
            final BufferedReader in2 = new BufferedReader(new InputStreamReader(p.getInputStream()));
            final BufferedReader err_in = new BufferedReader(new InputStreamReader(p.getErrorStream()));
            String line2;
            while ((line2 = in2.readLine()) != null) {
                if (line2.equals("/bin/sh: dvd-menu: command not found")) {
                    this.m_GUI.MessageBox("Could not locate dvd-menu in your path.\nPlease install all necessary dependencies\nand rerun dvd-homevideo.", 0);
                    in2.close();
                    err_in.close();
                    this.m_Error = true;
                }
                final StringTokenizer st = new StringTokenizer(line2);
                if (st.hasMoreTokens() && !st.nextToken().equals("Frame#")) {
                    this.m_GUI.txtAreaOutput.append(line2 + "\n");
                    this.m_GUI.txtAreaOutput.setCaretPosition(this.m_GUI.txtAreaOutput.getDocument().getLength());
                }
            }
            p.waitFor();
            p = Runtime.getRuntime().exec("mv dvd-menu.log log/", null, new File(this.m_GUI.strOutputDir));
            final File CreateOutDir = new File(this.m_GUI.strOutputDir + "/dvd_fs");
            if (CreateOutDir.exists() && CreateOutDir.isDirectory()) {
                CreateOutDir.delete();
            }
            Thread.sleep(2000L);
        }
        catch (IOException ex2) {
            SaveStackTrace.printTrace(this.m_GUI.strOutputDir, ex2);
            this.m_GUI.MessageBox(this.baseErr + "IO Error\n" + ex2.toString(), 0);
            ex2.printStackTrace();
            this.m_Error = true;
        }
        catch (InterruptedException ex3) {
            SaveStackTrace.printTrace(this.m_GUI.strOutputDir, ex3);
            this.m_GUI.MessageBox(this.baseErr + "dvd-homevideo thread was interrupted\n" + ex3.toString(), 0);
            ex3.printStackTrace();
            this.m_Error = true;
        }
    }
    
    public boolean createXML() {
        final File xmlFile = new File(this.m_GUI.strOutputDir + "/vmgm.xml");
        final File ListDir = new File(this.m_GUI.strOutputDir);
        final FilenameFilter filter = new FilenameFilter() {
            boolean ret_val = true;
            
            @Override
            public boolean accept(final File dir, final String name) {
                if (name.endsWith("vob")) {
                    if (!name.equals("menu.vob")) {
                        this.ret_val = true;
                    }
                    else {
                        this.ret_val = false;
                    }
                }
                else {
                    this.ret_val = false;
                }
                return this.ret_val;
            }
        };
        this.video_files = ListDir.list(filter);
        try {
            final BufferedWriter writer = new BufferedWriter(new FileWriter(xmlFile));
            writer.write("<dvdauthor dest=\"" + this.m_GUI.strOutputDir + "/DVD/\" jumppad=\"0\">");
            writer.newLine();
            writer.write("\t<vmgm>");
            writer.newLine();
            writer.write("\t\t<menus>");
            writer.newLine();
            writer.write("\t\t\t<pgc entry=\"title\" >");
            writer.newLine();
            writer.write("\t\t\t\t<vob file=\"" + this.m_GUI.strOutputDir + "/menu.vob\" pause=\"inf\" />");
            writer.newLine();
            if (this.titles[0] == null) {
                for (int i = 1; i <= this.video_files.length; ++i) {
                    writer.write("\t\t\t\t<button>jump title " + i + ";</button>");
                    writer.newLine();
                }
            }
            else {
                for (int i = 1; i < this.titles.length; ++i) {
                    if (!this.titles[i - 1].equals("BLANK") && !this.titles[i - 1].equals("DONE")) {
                        writer.write("\t\t\t\t<button>jump title " + i + ";</button>");
                        writer.newLine();
                    }
                    else if (this.titles[i - 1].equals("DONE")) {
                        break;
                    }
                }
            }
            writer.write("\t\t\t\t<post> jump vmgm menu 1; </post>");
            writer.newLine();
            writer.write("\t\t\t</pgc>");
            writer.newLine();
            writer.write("\t\t</menus>");
            writer.newLine();
            writer.write("\t</vmgm>");
            writer.newLine();
            writer.write("\t<titleset>");
            writer.newLine();
            writer.write("\t<titles>");
            writer.newLine();
            int i;
            for (i = 1; i < this.video_files.length; ++i) {
                writer.write("\t\t<pgc>");
                writer.newLine();
                writer.write("\t\t\t<vob file=\"" + this.video_files[i - 1] + "\" />");
                writer.newLine();
                writer.write("\t\t\t<post>jump title " + (i + 1) + ";</post>");
                writer.newLine();
                writer.write("\t\t</pgc>");
                writer.newLine();
            }
            writer.write("\t\t<pgc>");
            writer.newLine();
            writer.write("\t\t\t<vob file=\"" + this.video_files[i - 1] + "\" />");
            writer.newLine();
            writer.write("\t\t\t<post>call vmgm menu 1;</post>");
            writer.newLine();
            writer.write("\t\t</pgc>");
            writer.newLine();
            writer.write("\t</titles>");
            writer.newLine();
            writer.write("\t</titleset>");
            writer.newLine();
            writer.write("</dvdauthor>");
            writer.newLine();
            writer.close();
        }
        catch (IOException ex) {
            SaveStackTrace.printTrace(this.m_GUI.strOutputDir, ex);
            this.m_GUI.MessageBox(this.baseErr + "IO Error\n" + ex.toString(), 0);
            ex.printStackTrace();
            return true;
        }
        return false;
    }
}
