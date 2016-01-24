function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var app = angular.module('onlineParser', ['ngFileUpload']);



app.controller('ParserCtrl', ['$scope', 'Upload', function ($scope, Upload, $timeout) {
    $scope.rows = []
    $scope.uploadFiles = function(file, errFiles) {
        $scope.f = file;
        $scope.errFile = errFiles && errFiles[0];
        if (file) {
            file.upload = Upload.upload({
                url: '/parser/upload',
                data: {file: file, _xsrf: getCookie("_xsrf")}
            });

            file.upload.then(function (response) {
                $scope.rows = response.data;
            }, function (response) {
                if (response.status > 0)
                    $scope.errorMsg = response.status + ': ' + response.data;
            }, function (evt) {
                file.progress = Math.min(100, parseInt(100.0 *
                                         evt.loaded / evt.total));
            });
        }
    }
}]);