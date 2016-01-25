# Online Parser
* a user can upload a TSV file
* a user can view a table of content
* a user can move between pages

### Author
* Jongwook Kim fantazic@gmail.com

### System
* Web Sockets on Tornado web server
    * web socket for bidirectional communication
    * transfer a TSV file and render a page of whole data
    * keep the file in memory for each connection
* AngularJS and Bootstrap
    * ng-file-upload
    * pagination