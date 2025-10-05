import { deleteAsync } from 'del';
const targetPath = './static/lib/';

export default function clean(cb) {
    return deleteAsync(targetPath + '**/*').then(() => {
        cb()
    })
};