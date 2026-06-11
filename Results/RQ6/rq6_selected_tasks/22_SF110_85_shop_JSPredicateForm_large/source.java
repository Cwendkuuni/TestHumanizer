package umd.cs.shop;

import java.util.*;
import java.io.*;

public class JSPredicateForm extends Vector
{
    JSPredicateForm() {
    }
    
    public JSPredicateForm(final String text) {
        if (text != null) {
            this.JSPredicateFormInit(new StreamTokenizer(new StringReader(text)));
        }
    }
    
    public JSPredicateForm(final StreamTokenizer tokenizer) {
        this.JSPredicateFormInit(tokenizer);
    }
    
    void JSPredicateFormInit(final StreamTokenizer tokenizer) {
        if (tokenizer == null) {
            throw new JSParserError();
        }
        if (!JSUtil.expectTokenType(JSJshopVars.leftPar, tokenizer, "expected '('")) {
            throw new JSParserError();
        }
        if (!JSUtil.readToken(tokenizer, "Reading Predicate")) {
            throw new JSParserError();
        }
        if (tokenizer.ttype == JSJshopVars.rightPar) {
            JSUtil.println("Unexpected ) while reading Predicate");
            throw new JSParserError();
        }
        if (tokenizer.ttype == JSJshopVars.exclamation) {
            if (!JSUtil.expectTokenType(-3, tokenizer, "Operator name expected")) {
                throw new JSParserError();
            }
            tokenizer.pushBack();
            final String w = JSUtil.readWord(tokenizer, "JSPredicateForm");
            if (w.equals("%%%")) {
                throw new JSParserError();
            }
            this.addElement("!" + w);
        }
        else if (tokenizer.ttype == -3 && tokenizer.sval.equalsIgnoreCase("not")) {
            this.addElement(new String(tokenizer.sval));
            this.addElement(new JSPredicateForm(tokenizer));
            if (JSUtil.expectTokenType(JSJshopVars.rightPar, tokenizer, "JSPredicateForm")) {
                return;
            }
            throw new JSParserError();
        }
        else {
            if (tokenizer.ttype == -3 && tokenizer.sval.equalsIgnoreCase("call")) {
                this.addElement(new String(tokenizer.sval));
                tokenizer.ttype = JSJshopVars.leftPar;
                tokenizer.pushBack();
                final JSTerm t = new JSTerm(tokenizer);
                t.makeEval(true);
                this.addElement(t);
                return;
            }
            if (tokenizer.ttype != -3) {
                JSUtil.println("PlanningDomain: error");
                throw new JSParserError();
            }
            tokenizer.pushBack();
            final String w = JSUtil.readWord(tokenizer, "JSPredicateForm");
            if (w.equals("%%%")) {
                throw new JSParserError();
            }
            this.addElement(w);
        }
        if (!JSUtil.readToken(tokenizer, "JSPredicateForm")) {
            throw new JSParserError();
        }
        while (tokenizer.ttype != JSJshopVars.rightPar) {
            tokenizer.pushBack();
            this.addElement(new JSTerm(tokenizer));
            if (!JSUtil.readToken(tokenizer, "JSPredicateForm")) {
                throw new JSParserError();
            }
        }
    }
    
    public void print() {
        if (this.size() == 0) {
            JSUtil.println("Predicateform.print(): 0 elements");
            return;
        }
        final String str = this.elementAt(0);
        JSUtil.print("(");
        JSUtil.print(str + " ");
        if (str.equalsIgnoreCase("not")) {
            final JSPredicateForm el = this.elementAt(1);
            el.print();
        }
        else {
            for (short i = 1; i < this.size(); ++i) {
                final JSTerm el2 = this.elementAt(i);
                el2.print();
            }
        }
        JSUtil.print(" ) ");
    }
    
    public StringBuffer toStr() {
        final StringBuffer res = new StringBuffer();
        if (this.size() == 0) {
            JSUtil.println("Predicateform.print(): 0 elements");
            return res;
        }
        res.append("(");
        final String str = this.elementAt(0);
        res.append(str);
        if (str.equalsIgnoreCase("not")) {
            final JSPredicateForm el = this.elementAt(1);
            res.append(el.toStr());
        }
        else {
            for (short i = 1; i < this.size(); ++i) {
                final JSTerm el2 = this.elementAt(i);
                res.append(el2.toStr());
            }
        }
        res.append(")");
        return res;
    }
    
    public JSPredicateForm clonePF() {
        final JSPredicateForm np = new JSPredicateForm();
        final String str = this.elementAt(0);
        if (str.equalsIgnoreCase("not")) {
            np.addElement(this.elementAt(0));
            final JSPredicateForm el = this.elementAt(1);
            np.addElement(el.clonePF());
        }
        else {
            np.addElement(this.elementAt(0));
            for (short i = 1; i < this.size(); ++i) {
                final JSTerm ti = this.elementAt(i);
                np.addElement(ti.cloneT());
            }
        }
        return np;
    }
    
    public JSPredicateForm applySubstitutionPF(final JSSubstitution alpha) {
        final JSPredicateForm np = new JSPredicateForm();
        final String str = this.elementAt(0);
        if (str.equalsIgnoreCase("not")) {
            np.addElement(this.elementAt(0));
            final JSPredicateForm el = this.elementAt(1);
            np.addElement(el.applySubstitutionPF(alpha));
        }
        else {
            np.addElement(this.elementAt(0));
            for (short i = 1; i < this.size(); ++i) {
                final JSTerm ti = this.elementAt(i);
                np.addElement(ti.applySubstitutionT(alpha));
            }
        }
        return np;
    }
    
    public JSSubstitution matches(final JSPredicateForm t) {
        return this.matches(t, new JSSubstitution());
    }
    
    public JSSubstitution matches(final JSPredicateForm t, final JSSubstitution alpha) {
        JSSubstitution beta = new JSSubstitution();
        if (this.size() != t.size()) {
            beta.assignFailure();
            return beta;
        }
        final String functor = this.elementAt(0);
        if (!functor.equalsIgnoreCase(t.elementAt(0))) {
            beta.assignFailure();
            return beta;
        }
        if (functor.equalsIgnoreCase("not")) {
            final JSPredicateForm e1 = this.elementAt(1);
            final JSPredicateForm e2 = t.elementAt(1);
            beta = e1.matches(e2, alpha);
            return beta;
        }
        JSSubstitution gama = new JSSubstitution();
        final JSSubstitution newAlpha = alpha.cloneS();
        for (short i = 1; i < this.size(); ++i) {
            final JSTerm ti = this.elementAt(i);
            if (!ti.equals(t.elementAt(i))) {
                gama = ti.matches(t.elementAt(i), newAlpha);
                if (gama.fail()) {
                    return gama;
                }
                beta.addElements(gama);
                newAlpha.addElements(gama);
            }
        }
        return beta;
    }
    
    public boolean equals(final JSPredicateForm t) {
        if (t == null) {
            return false;
        }
        final String functor = this.elementAt(0);
        if (this.size() != t.size()) {
            return false;
        }
        final String functor2 = t.elementAt(0);
        if (!functor.equalsIgnoreCase(functor2)) {
            return false;
        }
        if (functor.equalsIgnoreCase("not")) {
            final JSPredicateForm e1 = this.elementAt(1);
            final JSPredicateForm e2 = t.elementAt(1);
            return e1.equals(e2);
        }
        for (short i = 1; i < this.size(); ++i) {
            final JSTerm ti = this.elementAt(i);
            final JSTerm oti = t.elementAt(i);
            if (!ti.equals(oti)) {
                return false;
            }
        }
        return true;
    }
    
    public JSPredicateForm standarizerPredicateForm() {
        final JSPredicateForm nTA = new JSPredicateForm();
        final String str = this.elementAt(0);
        if (str.equalsIgnoreCase("not")) {
            nTA.addElement(this.elementAt(0));
            final JSPredicateForm el = this.elementAt(1);
            nTA.addElement(el.standarizerPredicateForm());
            return nTA;
        }
        nTA.addElement(this.elementAt(0));
        for (short i = 1; i < this.size(); ++i) {
            final JSTerm ti = this.elementAt(i);
            nTA.addElement(ti.standardizerTerm());
        }
        return nTA;
    }
}
