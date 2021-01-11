odoo.define('payslip_import.trip_import_button', function (require) {
    "use strict";

    const core = require('web.core');
    const ListController = require('web.ListController');
    const ListView = require('web.ListView');
    const viewRegistry = require('web.view_registry');

    const QWeb = core.qweb;

    const TripListController = ListController.extend({
        /**
         * Extends the renderButtons function of ListView by adding a button
         * on the payslip list.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            this.$buttons.append($(QWeb.render("TripTreeView.trip_import_wizard", this)));
            const self = this;
            this.$buttons.on('click', '.btn_trip_import_wizard', function () {
                return self._rpc({
                    model: 'trip.import',
                    method: 'action_import_trip',
                }).then(function (results) {
                    self.do_action(results);
                });
            });
        }
    });

    const TripListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TripListController,
        }),
    });

    viewRegistry.add('trip_import_tree', TripListView);
});
