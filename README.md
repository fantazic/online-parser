# Online Parser
* a user can upload a TSV file
* a user can view a table of content
* a user can move between pages
* a user can share the page with others
    * every action is synced among shared users

### Author
* Jongwook Kim fantazic@gmail.com

### System
* Web Sockets on Tornado web server
    * web socket for bidirectional communication
    * transfer a TSV file and render a page of whole data
    * keep the file in memory for each connection
* AngularJS and Bootstrap
    * ng-file-upload
    * ui-bootstrap for pagination
    
### Demo
* [Live Demo](http://catlog.kr/parser/)
* test with [this sample file](https://github.com/fantazic/online-parser/tree/master/sample/sample.tsv)

### Nginx
If you want to use NGINX for proxy, check these pages.
* proxy websocketws: [websocket proxy setting](https://www.nginx.com/blog/websocket-nginx/)
* If you get 403 status: [websocket origin check](http://stackoverflow.com/questions/24800436/under-tornado-v4-websocket-connections-get-refused-with-403)
