package jaw.entrada;

import jaw.metamodelo.*;
import jaw.gui.*;
import java.util.*;
import jaw.*;
import javax.swing.filechooser.*;
import java.awt.*;
import javax.swing.*;
import java.io.*;

public class Salvar
{
    private boolean vela;
    private String arquivo;
    public String xml;
    public List<Entidade> entidade;
    public static final int SALVAR_XML = 10;
    public static final int SALVAR = 20;
    public static final int SALVAR_COMO = 30;
    
    public Salvar(final ProcessarEntidades form, final int tipoSalvar) {
        this.vela = false;
        this.arquivo = "";
        this.xml = "";
        this.entidade = new Vector<Entidade>();
        try {
            this.entidade = form.getEntidades();
        }
        catch (Exception ex) {
            Main.janelaPrincipal.log(ex.toString());
            return;
        }
        final JFileChooser escolhedor = new JFileChooser();
        escolhedor.setCurrentDirectory(new File(Main.configuracao.getCaminhoDosProjetos()));
        if (tipoSalvar == 10) {
            escolhedor.setFileFilter(new Filtro2());
        }
        if (tipoSalvar == 20 || tipoSalvar == 30) {
            escolhedor.setFileFilter(new Filtro());
        }
        if (tipoSalvar == 10 || tipoSalvar == 30 || (tipoSalvar == 20 && form.getNomeArquivoSalvo().equals("Novo Projeto"))) {
            escolhedor.showSaveDialog(form);
            this.vela = true;
        }
        if (escolhedor.getSelectedFile() == null && form.getName().equals("")) {
            return;
        }
        if (this.vela) {
            if (escolhedor.getSelectedFile() == null) {
                return;
            }
            this.arquivo = escolhedor.getSelectedFile().getAbsolutePath();
        }
        else {
            this.arquivo = form.getNomeArquivoSalvo();
        }
        if (tipoSalvar == 20 || tipoSalvar == 30) {
            if (!this.arquivo.endsWith(".jaw") && this.vela) {
                form.setNomeArquivoSalvo(this.arquivo += ".jaw");
                this.vela = false;
            }
            else {
                this.arquivo = form.getNomeArquivoSalvo();
            }
            System.out.println(form.getNomeArquivoSalvo());
            final Serializacao salvar = new Serializacao();
            try {
                if (salvar.salvar(this.entidade, this.arquivo)) {
                    JOptionPane.showMessageDialog(form, "Arquivo salvo com sucesso!", "Jaw - Salvar", 1);
                }
            }
            catch (Exception ex2) {
                JOptionPane.showMessageDialog(null, "N\u00c3£o foi poss\u00c3\u00advel salvar esse arquivo\n Verifique o formato das entidades !", "Salvando Arquivo", 0);
                Main.janelaPrincipal.log(ex2.toString());
            }
        }
        if (tipoSalvar == 10) {
            if (!this.arquivo.endsWith(".jaw.xml")) {
                this.arquivo += ".jaw.xml";
            }
            final SerializacaoXML serializaXML = new SerializacaoXML();
            this.xml = serializaXML.entidades2XML(this.entidade);
            try {
                final FileWriter escrevedor = new FileWriter(this.arquivo);
                escrevedor.write(this.xml);
                escrevedor.flush();
                escrevedor.close();
                JOptionPane.showMessageDialog(form, "Arquivo Exportado com sucesso!", "Jaw - Salvar", 1);
            }
            catch (Exception e) {
                JOptionPane.showMessageDialog(form, "N\u00c3£o foi poss\u00c3\u00advel salvar esse arquivo\n Verifique o formato das entidades !", "Salvando Arquivo", 0);
                Main.janelaPrincipal.log(e.toString());
            }
        }
    }
    
    private class Filtro2 extends FileFilter
    {
        @Override
        public boolean accept(final File f) {
            return f.isDirectory() || f.getName().toLowerCase().endsWith(".jaw.xml");
        }
        
        @Override
        public String getDescription() {
            return "XML JAW files";
        }
    }
    
    private class Filtro extends FileFilter
    {
        @Override
        public boolean accept(final File f) {
            return f.isDirectory() || f.getName().toLowerCase().endsWith(".jaw");
        }
        
        @Override
        public String getDescription() {
            return "JAW files";
        }
    }
}
