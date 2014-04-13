
/**
 * Umożliwa przechowywanie koszyka jako plik cookie.
 */
CookieStorageProvider = function(cname, cpath) {
        var cookieName = cname;
        var cookiePath = cpath;
        
        var createCookie = function(name, value, expires, path) {
            var tmp = '';
            tmp += name + '=' + value + ';';
            if (expires != null) tmp += 'expires=' + expires + ';';
            if (path != null) tmp += 'path=' + path + ';';
            
            return tmp;
        }
        
        var setContent = function(value) {
            document.cookie = createCookie(cookieName, value, null, cookiePath);
        };
        
        var remove = function() {
            document.cookie = createCookie(cookieName, '', 'Thu, 01 Jan 1970 00:00:00 GMT', cookiePath);
        };
        
        var getContent = function() {
            function getCookie(name) {
                var value = "; " + document.cookie;
                var parts = value.split("; " + name + "=");
                if (parts.length == 2) return parts.pop().split(";").shift();
            }            
            
            var str = getCookie(cookieName);
            if (str == null || str == '') return {};
            return JSON.parse(str);
        };
        
        return {
            setContent: setContent,
            getContent: getContent,
            remove: remove,
        };
    };

/**
 * Implementacja koszyka.
 *
 * Sposób przechowywania danych może być modyfikowany, wymagane jest jedynie, żeby posiadał metody:
 *  setContent(content)
 *      przyjmującą jako argument słownik zapisany w JSON
 *  getContent()
 *      zwracającą słownik (zdekodowany, w sensie już obiekt)
 *  remove()
 *      usuwającą całą zawartość
 *
 * Ta implementacja koszyka wykorzystuje te metody. Przykładową implementacją przechowywacza danych
 * jest {@link CookieStorageProvider} umożliwiający przechowywanie koszyka jako pliku cookie.
 *
 * Koszyk jest tak napradę słownikiem, którego klucze to identyfikatory produktów, a wartościami jest
 * ilość tego produktu.
 */
var cart = (function() {
    var storage = CookieStorageProvider('cart', '/');
    
    /**
     * Dodaje produkt o zadanym identyfikatorze do koszyka.
     */
    var add = function(pid) {
        var content = storage.getContent();
     
        if (pid in content) {
            content[pid]++;
        } else {
            content[pid] = 1;
        }
        
        storage.setContent(JSON.stringify(content));
                
        return true;
    };
    
    /**
     * Usuwa produkt o zadanym identyfikatorze z koszyka.
     *
     * @return false jeśli produktu o zadanym ID nie ma w koszyku, true w przeciwnym wypadku
     */
    var remove = function(pid) {
        var content = storage.getContent();
    
        if (!(pid in content)) return false;
        
        delete content[pid];
        
        storage.setContent(JSON.stringify(content));
        
        return true;
    };
    
    /**
     * Uaktualnia (zmienia ilość) produktu o zadanym identyfikatorze.
     *
     * Jeśli nowa ilość jest > 0 ustawia ją, w przeciwnym wypadku usuwa produkt z koszyka.
     *
     * @return false jeśli produktu o zadanym ID nie ma w koszyku, true w przeciwnym wypadku
     */
    var update = function(pid, amount) {
        var content = storage.getContent();
    
        if (!(pid in content)) return false;
        
        if (amount > 0) {
            content[pid] = amount;
        } else {
            delete content[pid];
        }
        
        storage.setContent(JSON.stringify(content));
        
        return true;
    };
    
    var clear = function() {
        storage.setContent(JSON.stringify({}));
    };
        
    return {
        add: add,
        update: update,
        remove: remove,
        clear: clear,
    };
})();

