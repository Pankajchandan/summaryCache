
# coding: utf-8

# In[1]:


import BaseHTTPServer
import os
import socket
from threading import Thread
from multiprocessing import Process, Manager
import sys
import pickle
from bitarray import bitarray
from lib import check_filter_list
import requests


# In[2]:


def load_backup(filename):
    #print "loading summary cache from backup file: ",filename
    with open(filename, 'r') as save:
         return pickle.loads(save.read())


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
def run_port(sock):
    print "listening to TCP connections at port 9000......\n"
    while True:
        connection, client_address = sock.accept()
        print "connection from: ", client_address
        thread_add_filter = Thread(target = add_filter, args = (connection, client_address))
        thread_add_filter.start()
    
# method to add filters to dictionary
def add_filter(connection, client_address):
    filter_dict = {}
    data = connection.recv(4096)
    index_list = data.decode('utf-8') 
    index_data  = pickle.loads(index_list)
    if os.path.isfile("backup.txt"):
            filter_dict = load_backup("backup.txt")
    filter_dict[client_address[0]] = index_data
    connection.close()
    print filter_dict
    with open('backup.txt', 'w') as save:
            save.write(pickle.dumps(filter_dict))
        


# In[5]:


if __name__ == '__main__':
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = ('', 9000)
        sock.bind(server_address)
        sock.listen(1)
        print "port opened at 9000"
        ## spawn a new process to listen in a loop
        process_run_port = Process(target = run_port, args = (sock,))
        process_run_port.start()
        print "running http server on port 8080\n "
        serverAddress = ('', 8080)
        server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
        server.serve_forever()
        
    except KeyboardInterrupt:
        process_run_port.terminate()
        sock.close()
        process_run_port.terminate()
        print "port terminated at 9000...\n"
        print "http server terminated..."
        server.socket.close()
        pass


# In[ ]:




