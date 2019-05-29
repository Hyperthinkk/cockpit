odoo.define('mail.systray.MailServerConfig', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var QWeb = core.qweb;

/**
 * Menu item appended in the systray part of the navbar
 *
 * The menu item indicates the counter of needactions + unread messages in chat
 * channels. When clicking on it, it toggles a dropdown containing a preview of
 * each pinned channels (except mailbox and mass mailing channels) with a quick
 * link to open them in chat windows. It also contains a direct link to the
 * Inbox in Discuss.
 **/
var MessagingMenu = Widget.extend({
    name: 'messaging_menu1',
    template:'mail.systray.ServerConfigMenu',
    events: {
        'click .o_mail_preview': '_onClickPreview',
        'click .o_filter_button': '_onClickFilterButton',
        'click .o_new_message': '_onClickNewMessage',
        'click .o_mail_preview_mark_as_read': '_onClickPreviewMarkAsRead',
        'show.bs.dropdown': '_onShowDropdown',
    },
    /**
     * @override
     */
    willStart: function () {
        return $.when(this._super.apply(this, arguments), this.call('mail_service', 'isReady'));
    },
    /**
     * @override
     */
    start: function () {
        return this._super.apply(this, arguments);
    },




});



var MessagingMenu = new MessagingMenu(this, 4);
// Render and insert into DOM

MessagingMenu.appendTo(self.$('.o_menu_systray'));



});
