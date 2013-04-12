$(document).ready(function(){

function changeValue() {
	$("#button").val("Validado");
}
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
var args = {"_xsrf" : getCookie("_xsrf")};

$(".form").submit(function(e){
	
	e.preventDefault();
	$.ajax({
		type:"POST",
		url: "/box",
		data: $.param($('form input')),
		success: function() {
		$("#button").val("Validado");}
		});
});

});
