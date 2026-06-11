package ioproject.server.network;

import java.lang.ref.*;
import ioproject.common.network.*;
import java.util.*;

public class ClientGroup implements Iterable<Client>
{
    private ClientGroup parentGroup;
    private Set<WeakReference<ClientGroup>> subGroups;
    private Set<Client> clients;
    private ClientHandler handler;
    
    ClientGroup(final ClientGroup theParentGroup) {
        this.parentGroup = theParentGroup;
        this.subGroups = new LinkedHashSet<WeakReference<ClientGroup>>();
        this.clients = new LinkedHashSet<Client>();
        this.handler = null;
    }
    
    ClientGroup parentGroup() {
        return this.parentGroup;
    }
    
    synchronized boolean notifyMessageSent(final Client client, final Object message) {
        if (!this.clients.contains(client)) {
            return false;
        }
        boolean inSubGroup = false;
        for (final WeakReference<ClientGroup> groupReference : this.subGroups) {
            inSubGroup = (groupReference.get().notifyMessageSent(client, message) || inSubGroup);
        }
        if (!inSubGroup && this.handler != null) {
            this.handler.messageSent(client, message);
        }
        return true;
    }
    
    synchronized boolean notifyMessageReceived(final Client client, final Object message) {
        if (!this.clients.contains(client)) {
            return false;
        }
        boolean inSubGroup = false;
        for (final WeakReference<ClientGroup> groupReference : this.subGroups) {
            inSubGroup = (groupReference.get().notifyMessageReceived(client, message) || inSubGroup);
        }
        if (!inSubGroup && this.handler != null) {
            this.handler.messageReceived(client, message);
        }
        return true;
    }
    
    synchronized boolean notifyExceptionCaught(final Client client, final Throwable cause) {
        if (!this.clients.contains(client)) {
            return false;
        }
        boolean inSubGroup = false;
        for (final WeakReference<ClientGroup> groupReference : this.subGroups) {
            inSubGroup = (groupReference.get().notifyExceptionCaught(client, cause) || inSubGroup);
        }
        if (!inSubGroup && this.handler != null) {
            this.handler.exceptionCaught(client, cause);
        }
        return true;
    }
    
    @Override
    public Iterator<Client> iterator() {
        return Collections.unmodifiableSet((Set<? extends Client>)this.clients).iterator();
    }
    
    public synchronized boolean contains(final Client client) {
        return this.clients.contains(client);
    }
    
    public synchronized int size() {
        return this.clients.size();
    }
    
    public synchronized boolean add(final Client client) {
        final boolean parentContainsClient = this.parentGroup == null || this.parentGroup.contains(client);
        if (parentContainsClient) {
            this.clients.add(client);
        }
        if (this.handler != null) {
            this.handler.clientAdded(client);
        }
        return parentContainsClient;
    }
    
    public synchronized boolean remove(final Client client) {
        final boolean clientIsMember = this.clients.contains(client);
        if (clientIsMember) {
            this.clients.remove(client);
            for (final WeakReference<ClientGroup> subGroupReference : this.subGroups) {
                subGroupReference.get().remove(client);
            }
        }
        if (this.handler != null) {
            this.handler.clientRemoved(client);
        }
        return clientIsMember;
    }
    
    public synchronized ClientGroup createSubGroup() {
        final ClientGroup subGroup = new ClientGroup(this);
        this.subGroups.add(new WeakReference<ClientGroup>(subGroup));
        return subGroup;
    }
    
    public synchronized void addClientHandler(final ClientHandler aHandler) {
        this.handler = aHandler;
    }
}
