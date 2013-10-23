// Post Model
var Post = Backbone.Model.extend({});

// Post collections
var Posts = Backbone.Collection.extend({

    model: Post,

    initialize: function(models, options){
        this.query = options.query || '';
        this.next_url = null;
    },

    url: function(){
        return '/api/streams?'+this.query;
    },

    parse: function(resp){
        this.next_url = resp.meta.next_url;
        return resp.objects;
    }

});

// Item View

var itemTpl = '\
<li class="span3 item" id="item-<%= obj.id %>">\
    <div class="thumbnail">\
        <div class="boker-picture view-thumb" id="view-thumb4">\
        <a href="<%= obj.permalink %>" id="boker-main-pic4"><img alt="<%= obj.description %>" src="/images/<%= obj.photo.key %>?type=list&crop=1"/></a>\
        <% if(obj.can_like){ %>\
          <div class="mask m-button">\
          <span class="info">\
          <button class="btn btn-large btn-warning btn-like-list" data-boker="<%= obj.key %>" type="button">\
          <i class="icon-star icon-white"></i> Suka!\
          </button>\
          </span>\
          </div>\
        <% } %>\
    </div> \
    <h2 class="boker-name">\
    <a href="<%= obj.permalink %>"><%= obj.description %></a>\
    </h2>\
    <span><i class="icon-eye-open"></i> <%= obj.num_view %> <i class="icon-thumbs-up"></i> <%= obj.num_like %> <i class="icon-comment"></i> <%= obj.num_comment %></span>\
    <div class="sidebox" style="padding:8px; height:auto">\
        <a href="<%= obj.user.url %>" style="float:left; margin-top:5px">\
        <img src="http://graph.facebook.com/<%= obj.user.id %>/picture?type=square" width="36" height="36" class="avatar"/>\
        </a>\
        <span class="label" style="margin-top:7px"><%= obj.user.username %></span><br/>\
        <span style="margin-left:3px"><i class="icon-time time"></i> <%= obj.created %></span>\
        </div>\
    </div>\
</li>\
';