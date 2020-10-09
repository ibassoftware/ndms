odoo.define('payslip_import.tree_import_button', function (require) {
    "use strict";

    const core = require('web.core');
    const ListController = require('web.ListController');
    const ListView = require('web.ListView');
    const viewRegistry = require('web.view_registry');

    const QWeb = core.qweb;

    const PayslipListController = ListController.extend({
        /**
         * Extends the renderButtons function of ListView by adding a button
         * on the payslip list.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            this.$buttons.append($(QWeb.render("PayslipListView.paylip_import_wizard", this)));
            const self = this;
            this.$buttons.on('click', '.btn_payslip_import_wizard', function () {
                return self._rpc({
                    model: 'payslip.import',
                    method: 'action_import_payslip',
                }).then(function (results) {
                    self.do_action(results);
                });
            });
        }
    });

    const PayslipListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: PayslipListController,
        }),
    });

    viewRegistry.add('payslip_import_tree', PayslipListView);
});
