from flask import Blueprint, url_for, flash, redirect, abort
from datadrone.extensions import db
from datadrone.forms import AddTagForm
from datadrone.models import Tag, Item
from flask_login import current_user, login_required


bp = Blueprint("tags", __name__, url_prefix="/tags")


@bp.route("/add/<int:item_id>", methods=["POST"])
@login_required
def add(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)

    form = AddTagForm()

    if form.validate_on_submit():
        tag = Tag(item_id=item_id, name=form.tagname.data)
        db.session.add(tag)
        db.session.commit()
        flash("Tag has been added.", "success")
    else:
        flash("Tags needs to be between 1 and 32 characters long.",
              "error")

    return redirect(url_for("items.tags", item_id=item_id))


@bp.route("/<int:tag_id>/delete")
@login_required
def delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    if tag.item.owner != current_user:
        abort(403)

    tag.deleted = True
    db.session.commit()

    flash("Tag has been deleted.", "warning")
    return redirect(url_for("items.tags", item_id=tag.item.item_id))
