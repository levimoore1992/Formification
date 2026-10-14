from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildWithVueAssets(build_py):
    def run(self):
        relative = Path(
            "formification/static/admin/formification/vue-formification/dist"
        )
        assets = Path(__file__).parent / relative / "assets"
        if not list(assets.glob("index-*.js")) or not list(assets.glob("index-*.css")):
            raise RuntimeError(
                "Build the Vue admin with npm ci && npm run build before packaging."
            )
        public = Path(__file__).parent / "formification/static/formification/dist"
        if not (public / "form.js").exists() or not (public / "form.css").exists():
            raise RuntimeError("Build the public form assets before packaging.")
        if "Bootstrap" in (public / "form.css").read_text():
            raise RuntimeError(
                "Rebuild the public assets without Bootstrap before packaging."
            )
        # Clear deleted templates/styles and obsolete hashed assets on repeated builds.
        target = Path(self.build_lib) / "formification"
        if target.exists():
            shutil.rmtree(target)
        super().run()


setup(cmdclass={"build_py": BuildWithVueAssets})
