import os
from lenhttp import Application, Request, logger, Endpoint
try:
	from config import PORT, AVATARS_FOLDER
except ModuleNotFoundError:
	import shutil
	shutil.move("config.sample.py", "config.py")
	logger.warning(
		"You haven't change a config file name, we did it for you "
		"please fill it with your preferences and run main.py again!"
	)
	raise SystemExit

DEFAULT_AV = AVATARS_FOLDER + "-1.png"
CACHED_DEFAULT = b""

# Check if defualt avatar exist.
if not os.path.exists(DEFAULT_AV):
    logger.error(
        f"You have not set a default avatar! Please create a file at {DEFAULT_AV} "
        "and try again!"
    )
    raise SystemExit

# Pre cache default avatar.
with open(DEFAULT_AV, "rb") as f: CACHED_DEFAULT = f.read()

async def serve_avatar(req: Request, u_id: str) -> bytes:
    """Handles all avatar requests to a.ppy.sh and serves the avatar."""
    using_gif = False

    # Check if we serve default avatar or user av.
    if numeric := u_id.isnumeric() and os.path.exists(
        av_loc := AVATARS_FOLDER + f"{u_id}.png"
    ):
        with open(av_loc, "rb") as f: avatar = f.read()
    
    # GIF support. Prob should be in a for loop for each filetype
    elif numeric and os.path.exists(
        av_loc := AVATARS_FOLDER + f"{u_id}.gif"
    ): 
        with open(av_loc, "rb") as f: avatar = f.read()
        using_gif = True

    # Serve them the cached default av.
    else: avatar = CACHED_DEFAULT
    
    # Send header so it gets treated as image.
    if using_gif and req.headers["User-Agent"] != "osu!":
        req.add_header("Content-Type", "image/gif")
    else:
        req.add_header("Content-Type", "image/png")
    return avatar

# Create the web server and assign all the routes.
app = Application(PORT, (Endpoint("/<id>", serve_avatar),))

# Add a middleware.
@app.add_middleware(404)
async def not_found(req: Request) -> bytes:
	"""Returns a default avatar."""

	req.add_header("Content-Type", "image/png")
	return CACHED_DEFAULT

app.start()
