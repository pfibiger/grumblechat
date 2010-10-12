var chat = function() {

    // private
    var update_interval_min = 1000;
    var update_interval_max = 1000 * 60;
    var update_interval_error = 1000 * 10;
    var update_interval = update_interval_min;
    var message_display_max = 70;
    var do_polling = true;

    var room;
    var account;
    var url_message_next;
    var $chatlog;
    var $msg_template;
    var $text_entry_content;

    function textEntrySubmit() {
        var msg = $text_entry_content.val();
        if (msg.length > 0) {
            sendMessage(msg);
            $text_entry_content.val('');
            update_interval = update_interval_min; // FIXME need to cancel pending update and retrigger it with this new interval
        }
        return false;
    }

    function scrollToBottom() {
        // trim message list
        var $messages = $chatlog.find('.message:visible');
        if ($messages.length > message_display_max) {
            $messages.slice(0, $messages.length - message_display_max).remove();
        }
        // scroll to bottom
        var dest = $('html').attr('scrollHeight') - $('html').attr('clientHeight');
        $('html').scrollTop(dest);
        $('body').scrollTop(dest); // FIXME this is a chromium workaround for bug #2891
    }

    function sendMessage(msg) {
        var $msg_new = $msg_template.clone();
        var myDate = new Date();

        function success(data) {
            do_polling = true;
            message = $.parseJSON(data);
            var $new_id = "message-" + account.nickname + "-" + message.id;
            $msg_new.attr("id",$new_id);
        }

        function error() {
            alert('failure');
            do_polling = true;
        }

        $msg_new.css('display', '');
        $msg_new.attr("id","message-temp-local");
        $msg_new.find('.msg-timestamp').html(formatTime(myDate));
        $msg_new.find('.msg-sender').html(account.nickname);
        $msg_new.find('.msg-content').html(msg);
        $msg_template.before($msg_new);
        scrollToBottom();
        var post_url = '/api/room/' + room.key + '/msg/';
        do_polling = false;
        $.ajax({
            url: post_url,
            type: "POST",
            data: { message: msg },
            success: success,
            error: error,
        });
        return false;
    }

    function updateChat() {

        function success(data) {
            if (data.messages) {
                $.each(data.messages, function (index, message) {
                    switch(message.event) {               
                    case 'topic':
                        $('#room-topic').text(message.content);
                        document.title = room.name + ' - ' + message.content;
                        break;
                    case 'part':
                        var $removeuser = 'user-' + message.sender_name;
                        $("#" + $removeuser).remove();
                        break;
                    case 'join':
                        var $adduser = 'user-' + message.sender_name;
                        if ($("#" + $adduser).length == 0){
                            $tablerow_toinsert = '<tr id="user-' + message.sender_name + '"><td>' +  message.extra + ' ' + message.sender_name + '</td></tr>';
                            $('#userlist tr:last').after($tablerow_toinsert);
                        }
                        break;
                    default:
                        break;
                    }
                    //always do 'message' type
                    var $match_id = "message-" + message.sender_name + "-" + message.id;
                    var $found_message = $('#' + $match_id);
                    if ($found_message.length != 0) {
                        // for now, lets update the content (until we do it in js)
                        $found_message.find('.msg-content').html(message.content);
                    } 
                    else {
                        var $msg_new = $msg_template.clone();
                        $msg_new.css('display', '');
                        $msg_new.addClass('event-' + message.event);
                        $msg_new.find('.msg-timestamp').html(formatTime(parseDate(message.timestamp)));
                        $msg_new.find('.msg-sender').html(message.sender_name);
                        $msg_new.find('.msg-content').html(message.content);
                        $msg_template.before($msg_new);
                    }
                });
                scrollToBottom();
                url_message_next = data.next;
                update_interval = update_interval_min;
            } else {
                // FIXME: we've temporarily changed the backoff from exponential to linear. + 2000 instead of * 2
                update_interval = Math.min(update_interval + 2000, update_interval_max);
            }
            setTimeout(updateChat, update_interval);
        }

        function error(request, status, error) {
            // give the server/network/etc some time to settle before retrying
            update_interval = update_interval_error;
            setTimeout(updateChat, update_interval);
            // TODO inform the user about the problem
        }

        $.ajax({
            url: url_message_next,
            dataType: 'json',
            success: success,
            error: error,
        });
    }

    function parseDate(str) {
        /* From http://anentropic.wordpress.com/2009/06/25/javascript-iso8601-parser-and-pretty-dates/
        Parses an ISO8601-formated date in UTC, i.e. yyyy-mm-ddThh:mm:ss.ssssss . */
            
        var parts = str.split('T'),
        dateParts = parts[0].split('-'),
        timeParts = parts[1].split(':'),
        timeSecParts = timeParts[2].split('.'),
        timeHours = Number(timeParts[0]),
        date = new Date;

        date.setUTCFullYear(Number(dateParts[0]));
        date.setUTCMonth(Number(dateParts[1])-1);
        date.setUTCDate(Number(dateParts[2]));
        date.setUTCHours(Number(timeHours));
        date.setUTCMinutes(Number(timeParts[1]));
        date.setUTCSeconds(Number(timeSecParts[0]));
        if (timeSecParts[1]) {
            date.setUTCMilliseconds(Math.round(Number(timeSecParts[1])/1000));
        }

        // by using setUTC methods the date has already been converted to local time
        return date;
    }

    function formatTime(date) {
        var parts = [date.getHours(), date.getMinutes(), date.getSeconds()];

        for (var i=0; i<parts.length; i++) {
            parts[i] = parts[i].toString();
            if (parts[i].length == 1)
                parts[i] = '0' + parts[i];
        }

        return parts.join(':');
    }

    function initialize(the_room, the_account, message_last_key) {
        // initialize "statics"
        room = the_room;
        account = the_account;
        url_message_next = '/api/room/' + room.key + '/msg/?since=' + message_last_key;
        $chatlog = $('#chatlog');
        $msg_template = $chatlog.find('.message').last();
        $text_entry_content = $('#text-entry-content');

        // apply jquery hooks and behaviors
        $('#room-topic').editable('/api/room/' + room.key + '/topic', {
            indicator   : 'Saving...',
            tooltip     : 'Click to edit',
            name        : 'topic',
            ajaxoptions : { dataType: 'json' },
            callback    : function (value, settings) { $(this).html(value.message) },
        });
        $('#text-entry').submit(textEntrySubmit);

        // prepare the window for user interaction
        scrollToBottom();
        $('#text-entry-content').focus();

        // start the update loop rolling
        setTimeout(updateChat);    
    }


    // public
    return {
        initialize: initialize,
    };

}();
