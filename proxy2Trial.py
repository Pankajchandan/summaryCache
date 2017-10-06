
# coding: utf-8

# In[1]:


import BaseHTTPServer
import os
import socket
from threading import Thread
import sys
import pickle
from bitarray import bitarray
from lib import check_filter_list
import time


# In[2]:


def load_backup(filename):
    #print "loading summary cache from backup file: ",filename
    with open(filename, 'rb') as save:
         return pickle.load(save)


# In[3]:


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    # Handle a GET request.
    def do_GET(self):
        try:
            ## figure out cache folder name
            cache_name = self.path.split("/")[2]
            
            ## Figure out what exactly is being requested. This is the full path where file should exist
            full_path = os.getcwd()+"/cache/"+cache_name+"/"+"index.html"
            
            ## It doesn't exist...i.e not in the localcache
            if not os.path.exists(full_path):
                print "not found in local cache"
                raise ServerException("'{0}' not found".format(self.path))
                
            ## ...if the file exists in cache
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            
            # ...it's something we don't handle.
            else:
                raise ServerException("Unknown object '{0}'".format(self.path))
                
        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)
    
    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)
    
    Error_Page = """        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content)
    
    # Handle unknown objects.
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    # Send actual content.
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


# In[4]:


# Run local tcp sever at port 9000
def run_port(sock,filter_dict):
    global close_port
    print "listening to TCP connections on port 9000......\n"
    while True:
        connection, client_address = sock.accept()
        if close_port == 1:
            print "close_port = 1; port terminated on 9000...\n"
            sock.close()
            break
        print "connection from: ", client_address, "\n"
        thread_add_filter = Thread(target = add_filter, args = (connection, client_address))
        thread_add_filter.start()
        thread_add_filter.join()
        
# method to terminate port
def port_close():
    global close_port
    close_port = 1
    sock_close = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 9000)
    sock_close.connect(server_address)
    
# method to add filters to dictionary
def add_filter(connection, client_address):
    global filter_dict
    data = connection.recv(8192)
    index_list = data.decode('utf-8')
    index_data = pickle.loads(index_list)
    filter_dict[client_address[0]] = index_data
    connection.close()


# In[5]:


##method to run servers
def run_servers():
    
    global filter_dict
    global server
    global sock
    
    print "initial filterdict has: ", filter_dict,"\n"
        
    ##check backup file
    if os.path.isfile("backup.pickle"):
        print "initializing history....\n"
        filter_dict = load_backup("backup.pickle")
        print "history: ",filter_dict,"\n"
        
    ##run tcp server
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('', 9000)
    sock.bind(server_address)
    sock.listen(5)
    print "port opened on 9000...\n"
        
    ##spawn a new thread to listen in a loop
    thread_run_port = Thread(target = run_port, args = (sock,filter_dict))
    thread_run_port.start()
        
    ##run http server
    print "running http server on port 8080...\n "
    server.serve_forever()


# In[6]:


if __name__ == '__main__':
    
    ##declare filter dictionary
    filter_dict =  {}
    
    ##declare flag for closing port
    close_port = 0
    
    ##initialize tcp server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    ##initialize http server
    serverAddress = ('', 8080)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    
    try:
        run_servers()
    
    ##handle exceptions
    except KeyboardInterrupt:
        print "writing to file backup.pickle : ", filter_dict, "\n"
        print "saving filter before terminating...\n"
        with open("backup.pickle", 'wb') as save:
            pickle.dump(filter_dict,save)
        server.socket.close()
        print "http server terminated...\n"
        port_close()

