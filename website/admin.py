from flask import Blueprint, render_template, flash, send_from_directory, redirect
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Product, Order, Customer
from .forms import ShopItemsForm, OrderForm
from .import db

admin = Blueprint('admin', __name__)

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.is_admin:  # Allow only admins
        form = ShopItemsForm()

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_shop_item = Product(
                product_name=product_name,
                current_price=current_price,
                previous_price=previous_price,
                in_stock=in_stock,
                flash_sale=flash_sale,
                product_picture=file_path
            )

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'Product "{product_name}" added successfully!', "success")
                return redirect('/admin-page')
            except Exception as e:
                flash(f"Error adding product: {e}", "error")

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html')

@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.is_admin:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.is_admin:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)

        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder': item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.flash_sale.render_kw = {'placeholder': item_to_update.flash_sale}

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'

            file.save(file_path)

            try:
                Product.query.filter_by(id=item_id).update({
                    'product_name': product_name,
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'in_stock': in_stock,
                    'flash_sale': flash_sale,
                    'product_picture': file_path
                })
                db.session.commit()
                flash(f'Product "{product_name}" updated successfully!', "success")
                return redirect('/shop-items')
            except Exception as e:
                flash(f"Error updating product: {e}", "error")

        return render_template('update_item.html', form=form)

    return render_template('404.html')

@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.is_admin:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One Item deleted', "success")
            return redirect('/shop-items')
        except Exception as e:
            flash('Item not deleted!!', "error")

    return render_template('404.html')

@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.is_admin:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')

@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.is_admin:
        form = OrderForm()
        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Order {order_id} updated successfully!', "success")
                return redirect('/view-orders')
            except Exception as e:
                flash(f"Error updating order: {e}", "error")
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')

@admin.route('/customers')
@login_required
def display_customers():
    if current_user.is_admin:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')

@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.is_admin:
        return render_template('admin.html')
    return render_template('404.html')

@admin.route('/create-admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    from werkzeug.security import generate_password_hash

    admin_email = "rubelgado@gmail.com"
    admin_username = "admin"
    admin_password = "jojoyb"

    existing_admin = Customer.query.filter_by(email=admin_email).first()

    if not existing_admin:
        try:
            new_admin = Customer(
                email=admin_email,
                username=admin_username,
                password_hash=generate_password_hash(admin_password),
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            flash(f"Admin user '{admin_username}' created successfully!", "success")
        except Exception as e:
            flash(f"Error creating admin: {e}", "error")
    else:
        flash("Admin user already exists!", "info")

    return redirect('/admin-page')  