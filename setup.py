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
        # Repeated builds must not ship obsolete hashed entry points.
        target = Path(self.build_lib) / relative
        if target.exists():
            shutil.rmtree(target)
        super().run()


setup(cmdclass={"build_py": BuildWithVueAssets})
