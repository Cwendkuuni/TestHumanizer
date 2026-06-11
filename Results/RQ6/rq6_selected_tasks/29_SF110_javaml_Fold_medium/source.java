package net.sf.javaml.core;

import net.sf.javaml.distance.*;
import java.util.*;

class Fold implements Dataset
{
    private int[] indices;
    private Dataset parent;
    
    public Fold(final Dataset parent, final int[] indices) {
        this.indices = indices;
        this.parent = parent;
    }
    
    @Override
    public boolean add(final Instance i) {
        throw new UnsupportedOperationException("Cannot do this on a fold of a dataset");
    }
    
    @Override
    public SortedSet<Object> classes() {
        return this.parent.classes();
    }
    
    @Override
    public Dataset[] folds(final int numFolds, final Random rg) {
        throw new UnsupportedOperationException("Method is not yet implemented");
    }
    
    @Override
    public Instance instance(final int index) {
        return this.parent.instance(this.indices[index]);
    }
    
    @Override
    public Set<Instance> kNearest(final int k, final Instance inst, final DistanceMeasure dm) {
        throw new UnsupportedOperationException("Method is not yet implemented");
    }
    
    @Override
    public void add(final int index, final Instance element) {
        throw new UnsupportedOperationException("Cannot do this on a fold of a dataset");
    }
    
    @Override
    public boolean addAll(final Collection<? extends Instance> c) {
        throw new UnsupportedOperationException("Cannot do this on a fold of a dataset");
    }
    
    @Override
    public boolean addAll(final int index, final Collection<? extends Instance> c) {
        throw new UnsupportedOperationException("Cannot do this on a fold of a dataset");
    }
    
    @Override
    public void clear() {
        throw new UnsupportedOperationException("Cannot do this on a fold of a dataset");
    }
    
    @Override
    public boolean contains(final Object o) {
        throw new UnsupportedOperationException("Method is not yet implemented");
    }
    
    @Override
    public boolean containsAll(final Collection<?> c) {
        throw new UnsupportedOperationException("Method is not yet implemented");
    }
    
    @Override
    public Instance get(final int index) {
        return this.instance(index);
    }
    
    @Override
    public int indexOf(final Object o) {
        throw new UnsupportedOperationException("Method is not yet implemented");
    }
    
    @Override
    public boolean isEmpty() {
        return false;
    }
    
    @Override
    public Iterator<Instance> iterator() {
        return new FoldIterator();
    }
    
    @Override
    public int lastIndexOf(final Object o) {
        throw new UnsupportedOperationException("Method is not yet implemented");
    }
    
    @Override
    public ListIterator<Instance> listIterator() {
        return new FoldIterator();
    }
    
    @Override
    public ListIterator<Instance> listIterator(final int index) {
        return new FoldIterator(index);
    }
    
    @Override
    public boolean remove(final Object o) {
        throw new UnsupportedOperationException("You cannot do this on a fold.");
    }
    
    @Override
    public Instance remove(final int index) {
        throw new UnsupportedOperationException("You cannot do this on a fold.");
    }
    
    @Override
    public boolean removeAll(final Collection<?> c) {
        throw new UnsupportedOperationException("You cannot do this on a fold.");
    }
    
    @Override
    public boolean retainAll(final Collection<?> c) {
        throw new UnsupportedOperationException("You cannot do this on a fold.");
    }
    
    @Override
    public Instance set(final int index, final Instance element) {
        throw new UnsupportedOperationException("You cannot do this on a fold.");
    }
    
    @Override
    public int size() {
        return this.indices.length;
    }
    
    @Override
    public List<Instance> subList(final int fromIndex, final int toIndex) {
        throw new UnsupportedOperationException("You cannot do this on a fold.");
    }
    
    @Override
    public Object[] toArray() {
        final Object[] out = new Object[this.indices.length];
        for (int i = 0; i < this.size(); ++i) {
            out[i] = this.instance(i);
        }
        return out;
    }
    
    @Override
    public <T> T[] toArray(final T[] a) {
        final Vector<T> tmp = new Vector<T>();
        for (final Instance i : this) {
            tmp.add((T)i);
        }
        return tmp.toArray(a);
    }
    
    @Override
    public int noAttributes() {
        return this.parent.noAttributes();
    }
    
    @Override
    public int classIndex(final Object clazz) {
        return this.parent.classIndex(clazz);
    }
    
    @Override
    public Object classValue(final int index) {
        return this.parent.classValue(index);
    }
    
    @Override
    public Dataset copy() {
        final Dataset out = new DefaultDataset();
        for (final Instance i : this) {
            out.add(i.copy());
        }
        return out;
    }
    
    class FoldIterator implements ListIterator<Instance>
    {
        private int currentIndex;
        
        public FoldIterator(final int index) {
            this.currentIndex = 0;
            this.currentIndex = index;
        }
        
        public FoldIterator(final Fold fold) {
            this(fold, 0);
        }
        
        @Override
        public boolean hasNext() {
            return this.currentIndex < Fold.this.indices.length;
        }
        
        @Override
        public Instance next() {
            ++this.currentIndex;
            return Fold.this.instance(this.currentIndex - 1);
        }
        
        @Override
        public void remove() {
            throw new UnsupportedOperationException("You cannot do this on a fold.");
        }
        
        @Override
        public void add(final Instance arg0) {
            throw new UnsupportedOperationException("You cannot do this on a fold.");
        }
        
        @Override
        public boolean hasPrevious() {
            return this.currentIndex > 0;
        }
        
        @Override
        public int nextIndex() {
            return this.currentIndex;
        }
        
        @Override
        public Instance previous() {
            --this.currentIndex;
            return Fold.this.instance(this.currentIndex);
        }
        
        @Override
        public int previousIndex() {
            return this.currentIndex;
        }
        
        @Override
        public void set(final Instance arg0) {
            throw new UnsupportedOperationException("You cannot do this on a fold.");
        }
    }
}
