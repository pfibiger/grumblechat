chat = function() {

  // private


  // public
  return {

    parseDate: function parseDate(str) {
      /* From http://anentropic.wordpress.com/2009/06/25/javascript-iso8601-parser-and-pretty-dates/ .
         Parses an ISO8601-formated date in UTC, i.e.
         yyyy-mm-ddThh:mm:ss.ssssss . */

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
    },

    formatTime: function formatTime(date) {
      var parts = [date.getHours(), date.getMinutes(), date.getSeconds()];

      for (i=0; i<parts.length; i++) {
        parts[i] = parts[i].toString();
        if (parts[i].length == 1)
          parts[i] = '0' + parts[i];
      }

      return parts.join(':');
    },

  };

}();
