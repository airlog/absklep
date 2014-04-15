
var lastVisited = (function() {
    var storage = CookieStorageProvider('last_visited', '/');
        
    var add = function(id) {
        var content = storage.getContent();
		if ($.isEmptyObject(content)) {
			content = [id];
		}
        else if (content.indexOf(id) == -1) {
			content.unshift(id);
		}
		if (content.length > 5) {
			content.pop();			
		}
        storage.setContent(JSON.stringify(content));
                
        return true;
    };
    
    return {
        add: add,
    };
    
})();

