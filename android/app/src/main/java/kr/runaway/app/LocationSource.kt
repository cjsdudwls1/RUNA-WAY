package kr.runaway.app

import android.annotation.SuppressLint
import android.content.Context
import android.os.Looper
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.flow
import kr.runaway.core.Gpx

/** 1Hz 위치 샘플. 실시간(GPS)과 리플레이(GPX)가 같은 형식으로 코어에 들어간다. */
data class Fix(val t: Int, val lat: Double, val lon: Double, val accM: Double)

interface LocationSource { fun fixes(): Flow<Fix> }

/** FusedLocationProvider, 1초 간격, 고정밀. 포그라운드 서비스 안에서 수집. */
class FusedSource(private val ctx: Context) : LocationSource {
    @SuppressLint("MissingPermission")
    override fun fixes(): Flow<Fix> = callbackFlow {
        val client = LocationServices.getFusedLocationProviderClient(ctx)
        val req = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 1000L)
            .setMinUpdateIntervalMillis(1000L)
            .build()
        val t0 = System.currentTimeMillis()
        val cb = object : LocationCallback() {
            override fun onLocationResult(r: LocationResult) {
                val l = r.lastLocation ?: return
                val t = ((System.currentTimeMillis() - t0) / 1000L).toInt()
                trySend(Fix(t, l.latitude, l.longitude, if (l.hasAccuracy()) l.accuracy.toDouble() else 8.0))
            }
        }
        client.requestLocationUpdates(req, cb, Looper.getMainLooper())
        awaitClose { client.removeLocationUpdates(cb) }
    }
}

/** assets의 GPX를 1Hz로 재생. 실내에서 전체 루프를 검증하는 용도. speedup으로 배속. */
class ReplaySource(private val ctx: Context, private val asset: String, private val speedup: Int = 1) : LocationSource {
    override fun fixes(): Flow<Fix> = flow {
        val xml = ctx.assets.open(asset).bufferedReader().readText()
        val pts = Gpx.resample1Hz(Gpx.parse(xml))
        for (p in pts) {
            emit(Fix(p.t.toInt(), p.lat, p.lon, p.acc))
            delay(1000L / speedup)
        }
    }
}
