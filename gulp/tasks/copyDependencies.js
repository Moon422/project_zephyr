import gulp from 'gulp';
import filter from 'gulp-filter';
import { readFileSync } from 'fs';
import merge from 'merge2';
import rename from 'gulp-rename';

const pkg = JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf-8'));
const nodeModules = './node_modules/';
const targetPath = './static/lib/';

export default function copyDependencies() {
    return merge([
        //common dependencies
        gulp
            .src(`${nodeModules}/**`)
            .pipe(filter(Object.keys(pkg.dependencies).map(module => `${nodeModules}${module}/dist/**/*.min*`)))
            .pipe(rename(function (path) {
                path.dirname = path.dirname.replace(/\/dist/, '').replace(/\\dist/, '');
            }))
            .pipe(gulp.dest(targetPath)),
    ]);
}