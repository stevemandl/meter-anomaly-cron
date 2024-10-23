// anomalyDB.ts
// tools for interacting with the meter_anomalies table
import mysql from 'mysql2/promise';


// for connectivity to the trend database

const dbConfig = {
	connectionLimit: 10,
	host: process.env.TRENDDB_HOST,
	user: process.env.TRENDDB_USER,
	password: process.env.TRENDDB_PASSWORD,
	database: process.env.TRENDDB
};
export const pool = mysql.createPool(dbConfig);

// object literal acts as singleton export


function now() {
    return new Date().toISOString();
}

export async function getAnomalies(algorithm: string = "%", point: string = "%", openOnly: boolean = true) {
    const sql = 'select jdoc from meter_anomalies where _point like ? and _algorithm like ?'
        + (openOnly ? ' and _clear_ts is null' : '');
    const results = await pool.query(sql, [point, algorithm]);
    return results.rows.map(r => r.jdoc);
}

export async function clearAnomaly(id: number) {
    await pool.query(
        "UPDATE meter_anomalies SET jdoc = JSON_SET(jdoc, '$.clear_ts', ?) WHERE id = ?",
        [now(), id]
    );
}
export async function clearAllAnomalies() {
    await pool.query(
        "UPDATE meter_anomalies SET jdoc = JSON_SET(jdoc, '$.clear_ts', ?)",
        [now()]
    );
}
export async function deleteAnomaly(id: number) {
    await pool.query(
        "DELETE FROM meter_anomalies WHERE id = ?",
        [id]
    );
}
export async function deleteAllAnomalies() {
    await pool.query(
        "DELETE FROM meter_anomalies"
    );
}
export async function addAnomaly(jdoc: MeterAnomaly) {
    const res = await pool.query(
        "INSERT INTO meter_anomalies (jdoc) VALUES (?)",
        [JSON.stringify(jdoc)]
    );
    return res[0].insertId;
}
export async function getAnomaly(id: number) {
    const res = await pool.query(
        "SELECT jdoc FROM meter_anomalies WHERE id = ?",
        [id]
    );
    return res.rows[0].jdoc;
}

