#
def allowed_file(filename):
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def upload_file(item):
    # check if the post request has the file part
    if "foto" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["foto"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "":
        # flash("No selected file") # TODO: fix zthsi flash error on empty file
        return redirect(request.url)
    if file and allowed_file(file.filename):
        format = file.filename.split(".")[-1:]
        file_name = (
            f"{'_'.join(file.filename.split('.')[:-1])}_{datetime.datetime.utcnow()}.{format}"
        )
        filename = secure_filename(file_name)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        item.document_filename = filename
        db_session.commit()


@app.route("/uploads/<name>")
@login_required
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
