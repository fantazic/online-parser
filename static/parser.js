var app = angular.module('onlineParser', ['ngFileUpload', 'ui.bootstrap']);

app.controller('ParserCtrl', ['$scope', function ($scope) {
    $scope.ws;
    $scope.rows;
    $scope.currentPage;
    $scope.totalRows;
    $scope.maxSize = 5;
    $scope.itemsPerPage = 100;
    $scope.isConnected = false;

    $scope.init = function() {
        $scope.ws = new WebSocket('ws://' + location.host + '/parser/ws');
        $scope.ws.binaryType = 'arraybuffer';

        $scope.ws.onopen = function() {
            console.log('Connected.');
            $scope.isConnected = true;
        };
        $scope.ws.onmessage = function(evt) {
            console.log(evt.data);
            $scope.$apply(function () {
                message = JSON.parse(evt.data);
                $scope.currentPage = parseInt(message['page_no']);
                $scope.totalRows = parseInt(message['total_number']);
                $scope.rows = message['data'];
            });
        };
        $scope.ws.onclose = function() {
            console.log('Connection is closed...');
            $scope.isConnected = false;
        };
        $scope.ws.onerror = function(e) {
            console.log(e.msg);
        };
    }

    // this works for a smaller file
    // check how to upload slices of a file if you want to transfer a big file
    $scope.uploadFile = function(file, errFiles) {
        ws = $scope.ws;
        $scope.f = file;
        $scope.errFile = errFiles && errFiles[0];
        if (file) {
            reader = new FileReader();
            rawData = new ArrayBuffer();

            reader.onprogress = function(evt) {
                file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
            }
            reader.onload = function(evt) {
                rawData = evt.target.result;
                ws.send(rawData);
            }

            reader.readAsArrayBuffer(file);
        }
    }

    $scope.pageChanged = function() {
        ws = $scope.ws;
        console.log('currentPage: ' + $scope.currentPage);
        ws.send($scope.currentPage);
    }

    $scope.init();
}]);